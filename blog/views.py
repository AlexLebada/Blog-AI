from django.shortcuts import render, get_object_or_404, redirect
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from blog.models.posts import Post
from django.contrib.auth.models import User
from blog.models.chatbot import InputChatbot
import io
import base64

# Create your views functions here.
def index(request):
    posts = Post.objects.all()
    return render(request, 'login.html', {'posts': posts})


def post(request, slug):
    print(slug)
    posts = Post.objects.all()
    return render(request, 'post.html', {
        'post': get_object_or_404(Post, slug=slug),
        'posts': posts
    })


def chatbot_view(request):
    if request.method == 'POST':
        user_input = request.POST.get('large_text')  # Get the text from the form
        action = request.POST.get('action')  # Check which button was clicked
        print(user_input)

        if action == 'save':  # Save button was clicked
            InputChatbot.objects.create(text='text')  # Save input to the database
            return redirect('chatbot')  # Redirect to clear the form after submission

        elif action == 'clear':  # Clear button was clicked
            return redirect('chatbot')  # Just reload the page (no saving)

    # Pass data to the template (optional, e.g., show recent inputs)
    recent_inputs = InputChatbot.objects.all().order_by('-created_at')[:5]
    return render(request, 'profile.html', {
        'recent_inputs': recent_inputs,
    })




def about(request):
    return render(request, 'about.html', {})


def profile(request):
    posts = Post.objects.all()
    users = User.objects.all()
    user_post_counts = {}
    for user in users:
        user_post_counts[user.username] = Post.objects.filter(writer=user).count()

    print(user_post_counts)

    usernames = list(user_post_counts.keys())
    post_counts = list(user_post_counts.values())

    # Create the chart
    fig, ax = plt.subplots()
    ax.barh(usernames, post_counts, color='skyblue')
    ax.set_title('Posts by User')
    ax.set_xlabel('Number of Posts')
    ax.set_ylabel('Users')

    # Save the chart as a base64 string
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    chart_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()

    # Render the profile template with the chart
    return render(request, 'profile.html', {'chart': chart_base64})