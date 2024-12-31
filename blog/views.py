import time

from django.shortcuts import render, get_object_or_404, redirect
import matplotlib.pyplot as plt
import matplotlib
from django.contrib.auth.decorators import login_required
from .utils import chunks_text_file, write_to_mongodb, initiate, pipeline_embedder, fetch_from_mongodb, pipeline_RAG
matplotlib.use('Agg')
from blog.models.posts import Post
from django.contrib.auth.models import User
from blog.models.chatbot import UploadedFile
from blog.models.models import Writer
import io
import base64
from .utils import get_mongo_db
from openai import OpenAI
import pandas as pd
import os
from django.http import JsonResponse, HttpResponse
from .forms import ChatbotForm, PostForm
from django.views.decorators.csrf import csrf_exempt

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
waitProcessing = 0

# Create your views functions here.
def index(request):
    return render(request, './registration/login.html')


def settings(request):
    return render(request, 'settings.html')


def profile(request):
    return render(request, 'profile.html')


@login_required(login_url='/login/')
def voting(request):
    return render(request, 'voting_page.html')

def post(request, slug):
    print(slug)
    post = get_object_or_404(Post.objects.select_related('writer'), slug=slug)
    posts = Post.objects.filter(status='approved').select_related('writer')
    return render(request, 'post.html', {
        'post': post,
        'posts': posts
    })

#not used yet
def save_to_mongodb_2(request):
    if request.method == 'POST':
        data = {
            'name': request.POST.get('name'),
            'description': request.POST.get('description')
        }
        db = get_mongo_db()
        result = db.collection_name.insert_one(data)  # Replace 'collection_name' with your collection
        return JsonResponse({'message': 'Data saved!', 'id': str(result.inserted_id)})

    return JsonResponse({'error': 'Invalid request'}, status=400)

#not used yet
def fetch_from_mongodb_2():
    db = get_mongo_db()
    documents = db.collection_name.find({}, {'_id': 0})  # Replace 'collection_name' with your collection
    return JsonResponse({'documents': list(documents)})


def upload_file(request):
    global waitProcessing
    if waitProcessing == 1:
        return JsonResponse({'error': 'Processing in progress, please wait.'}, status=409)

    if request.method == 'POST' and request.FILES.get('file'):
        print("error")
        if request.POST.get('submit_file'):
            print("type: submit_file")
        uploaded_file_name = request.FILES['file']
        file_binary_content = uploaded_file_name.read()
        file_string_content = file_binary_content.decode('utf-8')

        # Save the file in the database; if multiple name exists, is changed adding some code;
        # I take this name for storing into db for RAG
        file_instance = UploadedFile.objects.create(file=uploaded_file_name, uploaded_by=request.user)
        file_name = os.path.basename(file_instance.file.name)
        print("filename: ", file_name)
        waitProcessing = 1
        try:
            status = initiate()
            print("status:", status)
            chunks = chunks_text_file(file_string_content)
            documents = pipeline_embedder(chunks)
            result = write_to_mongodb(file_name, documents)

            if result == 1:
                waitProcessing = 0
                return JsonResponse({'file_name': file_instance.file.name,
                                     'message': 'processing done'})
        except Exception as e:
            waitProcessing = 0  # Reset flag on error
            return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)

    return JsonResponse({'error': 'No file uploaded'}, status=400)


def all_posts(request):

    posts = Post.objects.filter(status='approved')
    return render(request, 'all_posts.html', {'posts': posts})


def home(request):
    return render(request, 'home.html', {})


def writer_panel(request):
    if not request.user.groups.filter(name='Writers').exists():
        return redirect('editor_panel')
    # .get() is better than request.POST['submit_chatbot'], as it return a None if no key found
    if request.method == 'POST' and request.POST.get('submit_chatbot'):
        option = request.POST.get('selected_option')
        user_input = request.POST['query']

        if option == 'option1':
            bot_response = get_chatgpt_answer(user_input)
        else:
            if request.POST.get('selected_dropdown'):
                file_name = request.POST.get('selected_dropdown')
            if request.POST.get('file_upload_value'):
                file_name = request.POST.get('file_upload_value')

        if option == 'option2':
            status = initiate()
            print("status:", status)
            docs = fetch_from_mongodb(file_name)
            bot_response = pipeline_RAG(docs, user_input)
        elif option == 'option3':
            bot_response = 'Not working yet'

        chatbot_form = ChatbotForm(data={
            'query': user_input,
            'answer': bot_response
        })
        if chatbot_form.is_valid():
            # Save the form to the database
            chatbot_form.save()
            return JsonResponse({'answer': bot_response})

        return JsonResponse({'error': 'Invalid data submitted'}, status=400)

    writer = Writer.objects.get(user=request.user)
    if request.method == 'POST' and request.POST.get('submit_post'):
        post_form = PostForm(data=request.POST, files=request.FILES)
        if post_form.is_valid():
            print("yes")
            post = post_form.save(commit=False)
            post.writer = writer
            post.save()
            writer.all_posts += 1
            writer.save()
            return JsonResponse({'message': 'Post created successfully!'})
        else:
            return JsonResponse({'error': 'Invalid form submission', 'details': post_form.errors}, status=400)
    else:
        post_form = PostForm()



    posts = Post.objects.filter(writer=writer)
    uploaded_files = UploadedFile.objects.filter(uploaded_by=request.user).values_list('file', flat=True)
    file_names = [os.path.basename(file) for file in uploaded_files]
    chart_base64 = PostCountChart()
    # Render the profile template with the chart
    return render(request, 'writer_panel.html', {'chart': chart_base64,
                                               'posts': posts,
                                               'file_names': file_names,
                                               'form': post_form,
                                               'writer': writer})


def editor_panel(request):
    posts = Post.objects.filter(status='for_approval').select_related('writer')
    is_reader = request.user.groups.filter(name="Readers").exists() if request.user.is_authenticated else False
    return render(request, 'editor_panel.html', {'posts': posts,
                                                 'is_reader': is_reader})

def get_chatgpt_answer(input_text: str, input_no_answers: int = 1):
    req_answers = input_no_answers
    csv_tokens_used = 100
    csv_model = 'gpt-4o'
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": input_text,
            }
        ],
        model=csv_model,
        max_tokens=csv_tokens_used,
        temperature=0.7,
        top_p=0.5,
        n=input_no_answers,
    )

    answers = [choice.message.content for choice in response.choices]
    # returns a list
    return answers

def PostCountChart():
    posts = Post.objects.all()
    writers = Writer.objects.all()
    user_post_counts = {}

    for writer in writers:
        # Count posts associated with each writer's user
        user_post_counts[writer.user] = Post.objects.filter(writer=writer).count()

    # Extract usernames (or user ids) and post counts
    usernames = [str(writer.user.username) for writer in writers]  # Get the username (or user.id if needed)
    post_counts = [user_post_counts.get(writer.user, 0) for writer in writers]  # Get the post count for each user

    # Create the chart
    fig, ax = plt.subplots(figsize=(3,2.5)) # width, height
    ax.barh(usernames, post_counts, color='skyblue')  # Horizontal bar chart
    ax.set_title('Posts by User')
    ax.set_xlabel('Number of Posts')
    ax.set_ylabel('Users')

    # Save the chart as a base64 string
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    chart = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()

    return chart
