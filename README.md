## Project description
 This is a blog application with the following functionalities:
 
 **1. ML tools**
-	Chatbot: for general q's
-	Answer based context: where creators can enhance their work by getting specific answers from chatbot with provided external data
-	Summarization: Extract main ideas of a content *(in progress)*

 **2. Login/logout**
 
 **3. User/Content management**
 - User groups: writers, readers, editors, admins (for admin panel)
 - Posts are displayed based on editor approval, while only writers can create them
 - Readers can only vote

 **4. Common chatbot interface for ML tools:** using javascript
    
 **5. Reward/token system:** as each usage of API endpoints of ML tools has a cost *(in progress)*
    
 **6. Storing data:** vector embeddings using Mongodb Atlas
<br>

## Backend description

* **Project urls**
  
    */Blog_2/url.py:*

       urlpatterns = [
        #re_path(r'^post/(.*)$', blog_views.post), #using regex pattern
        path('post/<slug:slug>/', blog_views.post), #without regex
        path('all_posts/', blog_views.all_posts),
        path('', blog_views.home, name='home'),
        #path('', blog_views.index),
        path('writer_panel/', blog_views.writer_panel, name='writer_panel'),
        path('editor_panel/', blog_views.editor_panel, name='editor_panel'),
        path('profile/', blog_views.profile, name='profile'),
        path('voting/', blog_views.voting, name='voting'),
        path('admin/', admin.site.urls),
        path('settings/', blog_views.settings, name='settings'),
        path('admin_tools_stats/', include('admin_tools_stats.urls')),
        path('register/', include('register.urls')),
        path('photo/upload/', room_views.photo_upload, name='photo_upload'),
        path('', include("django.contrib.auth.urls")),
        path('login/', LoginView.as_view(template_name='./registration/login.html'), name='login'),
        path('upload-file/', blog_views.upload_file, name='upload_file'),
      ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

 * **Apps structure**
   - blog: handles user interaction with app for content creation
   - register: user creation
   - room: interaction between users

  * **Models:** Post, InputChatbot, UploadedFile, Photo, Writer
  * **Forms:** RegisterForm, ChatbotForm, PostForm
  * **Views**
    - Writer_panel: Renders user panel for writers group. Here it process two different POST requests: for chatbot user input and return answer. Second is for post creation, using its defined form
    - Editor_panel: The endpoint where the editors group have access to give approval for posting content
    - Upload_file: I'm using a global variable to deny concurrent requests while previous request is processing the file for storage its content and corresponding embedding vectors
    - etc.
  * **Utility files:** in utils.py where are my functions for storing/fetching into/from MongoDB. Also here is my pipeline for chatbot and interaction with 3rd party API for ML models

<br> 

 ## Frontend description

<br>

![Screenshot 2024-12-31 142218](https://github.com/user-attachments/assets/b24f68bf-b985-4f21-919f-68f9f475bd52)

* ### Templates
  <img src="https://github.com/user-attachments/assets/8490b564-3bfa-4feb-b84f-e7fe17b4b167" width="800" height="250">


  - **User panel**

   Because I want to make custom POST requests without *writer_panel.html* page refresh, im using Fetch API when DOM loaded. For example, here Im making the request for post submission

   */Blog_2/blog/static/css/chatbot.js:*

           document.addEventListener('DOMContentLoaded', function() {
           ...
              postForm.addEventListener('submit', function (event) {
              event.preventDefault(); // Prevent page reload
      
              const formData = new FormData(postForm); // Collect form data including the file
              formData.append('submit_post', 'true')
              const csrfToken = getCSRFToken();
      
              fetch('/writer_panel/', {
                  method: 'POST',
                  headers: {
                      'X-CSRFToken': csrfToken, // Include CSRF token
                  },
                  body: formData,
              })
                  .then(response => response.json())
                  ...
              })
           })



