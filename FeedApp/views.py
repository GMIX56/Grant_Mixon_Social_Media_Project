from django.shortcuts import render, redirect
from .forms import PostForm,ProfileForm, RelationshipForm # importing forms created in forms.py
from .models import Post, Comment, Like, Profile, Relationship
from datetime import datetime, date

from django.contrib.auth.decorators import login_required
from django.http import Http404


# Create your views here.

# When a URL request matches the pattern we just defined, 
# Django looks for a function called index() in the views.py file. 

def index(request):
    """The home page for Learning Log."""
    return render(request, 'FeedApp/index.html')



@login_required # only can access after they have logged in
def profile(request): # control our access to the database and posting things to webpage and getting things from the webpage to our database
    profile = Profile.objects.filter(user=request.user) # request.user refer to person currently logged on, user = becuase it is one of the fields in the profile model (used to get profile)
                                                        # for some reason only filter works with exist, get does not work
    if not profile.exists(): # checking if statement about brought back data, see if profile exists, if not, does the below
        Profile.objects.create(user=request.user) # creates the user
    profile = Profile.objects.get(user=request.user) # get the profile of the user

    if request.method != 'POST': # if the request is not a post request, a post request is when the user submits information to the server
        form = ProfileForm(instance=profile) # instance = prepopulate the form with existing data from profile
    else:
        form = ProfileForm(instance=profile, data=request.POST) # populates the form with the data the user has submitted
        if form.is_valid(): # checking if the form is valid
            form.save() # saving the form to the database
            return redirect('FeedApp:profile') # redirecting to the profile page
    # in line because it has to be carried out no matter what 
    context = {'form': form} # context dictionary to pass to the template html file
    return render(request, 'FeedApp/profile.html', context) # renders the template with the context dictionary

@login_required # only can access after they have logged in
def myfeed(request): # see all our posts along with the likes and comments
    comment_count_list = [] # list to hold the number of comments for each post
    like_count_list = [] # list to hold the number of likes for each post
    posts = Post.objects.filter(username=request.user).order_by('-date_posted') # getting all the posts from the database, use filter to get all posts, - puts in descending order
    for p in posts:
        c_count = Comment.objects.filter(post=p).count() # counting the number of comments for each post, p is the post from the for loop above
        l_count = Like.objects.filter(post=p).count() # counting the number of likes for each post, p is the post from the for loop above
        comment_count_list.append(c_count) # appending the count to the list
        like_count_list.append(l_count) # appending the count to the list
    zipped_list = zip(posts,comment_count_list,like_count_list) # zipping the three lists together to pass to the template
    
    context = {'posts': posts, 'zipped_list': zipped_list} # context dictionary to pass to the template html file
    return render(request, 'FeedApp/myfeed.html', context) # renders the template with the context dictionary
