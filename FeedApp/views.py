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


@login_required
def new_post(request): # creating a new post
    if request.method != 'POST': # if the request is not a post request, a post request is when the user submits information to the server
        form = PostForm() # create a blank form
    else:
        form = PostForm(request.POST,request.FILES) # populates the form with the data submitted by the user, request.FILES is for the image upload
        if form.is_valid(): # checks if the form is valid
            new_post=form.save(commit=False) # same it, but not commit it to the database yet, because we don't have all the informaiton
            new_post.username = request.user # set the username field to the current user
            new_post.save() # now save it to the database
            return redirect('FeedApp:myfeed') # redirect to the myfeed page
    
    context = {'form':form} # context dictionary to pass to the template html file
    return render(request, 'FeedApp/new_post.html', context) # renders the template with the context dictionary

@login_required
def friendsfeed(request):
    comment_count_list = []
    like_count_list = []
    friends = Profile.objects.filter(user=request.user).values('friends')
    posts = Post.objects.filter(username__in=friends).order_by('-date_posted')
    for p in posts:
        c_count = Comment.objects.filter(post=p).count()
        l_count = Like.objects.filter(post=p).count()
        comment_count_list.append(c_count)
        like_count_list.append(l_count)
    zipped_list = zip(posts,comment_count_list,like_count_list)

    if request.method == 'POST' and request.POST.get('like'):
        post_to_like = request.POST.get("like")
        print(post_to_like)
        like_already_exists = Like.objects.filter(post_id=post_to_like,username=request.user)
        if not like_already_exists.exists():
            Like.objects.create(post_id=post_to_like,username=request.user)
            return redirect("FeedApp:friendsfeed")
    
    context = {'posts':posts, 'zipped_list':zipped_list}
    return render(request, 'FeedApp/friendsfeed.html', context)



# there is not a comments form in forms.py GO BACK TO THIS, going to create our own button and process it manually rather than rely on django
@login_required
def comments(request, post_id):
    if request.method == 'POST' and request.POST.get('btn1'): # checking if the request is a post request and if the button with name btn1 was clicked
        comment = request.POST.get("comment") # getting the comment from the form
        Comment.objects.create(post_id=post_id,username=request.user,text=comment, date_added=date.today()) # creating a new comment object and saving it to the database

    comments = Comment.objects.filter(post=post_id) # getting all the comments for the post with the given post_id
    post = Post.objects.get(id=post_id) # getting the post object with the given post_id

    context = {'post':post, 'comments':comments} # context dictionary to pass to the template html file
    return render(request, 'FeedApp/comments.html', context) # renders the template with the context dictionary

        

@login_required
def friends(request):
    #get the admin_profile and user profile to create the first relationship
    admin_profile = Profile.objects.get(user=1)
    user_profile = Profile.objects.get(user=request.user)

    # to get my friends
    user_friends = user_profile.friends.all()
    user_friends_profiles = Profile.objects.filter(user__in=user_friends)

    # to get Friend Requests sent
    user_relationships = Relationship.objects.filter(sender=user_profile)
    request_sent_profiles = user_relationships.values('receiver')

    # to get eligible profiles - exclude the user, their existing friends, and friend requests sent already
    all_profiles = Profile.objects.exclude(user=request.user).exclude(id__in=user_friends_profiles).exclude(id__in=request_sent_profiles)


    # to get friend requests received by the user
    request_received_profiles = Relationship.objects.filter(receiver=user_profile,status='sent')

    # if this is the first time to access the friend requests page, create the first relationship
    # # with the admin of the website (so the admin is friends with everyone)

    if not user_relationships.exists():              # 'filter' works with 'exists', 'get' does not
        Relationship.objects.create(sender=user_profile, receiver=admin_profile, status='sent')

    # check to see WHICH submit button was pressed (sending a friend request or accepting a friend request)

    # this is to process all send requests
    if request.method == 'POST' and request.POST.get("send_request"):
        receivers = request.POST.getlist("send_request")
        for receiver in receivers:
            receiver_profile = Profile.objects.get(id=receiver)
            Relationship.objects.create(sender=user_profile,receiver=receiver_profile,status='sent')
        return redirect('FeedApp:friends')


    # this is to process all receive requests
    if request.method =='POST' and request.POST.get("receive_request"):
        senders = request.POST.getlist("receive_request")
        for sender in senders:
            # update the relationship model for the sender to status accepted
            Relationship.objects.filter(id=sender).update(status='accepted')

            #create an relationship object to access the sender's user id
            # to add to the friends list of the user
            relationship_obj = Relationship.objects.get(id=sender)
            user_profile.friends.add(relationship_obj.sender.user)

            #add the user to the friends list of the sender's profile
            relationship_obj.sender.friends.add(request.user)

    context = {'user_friends_profiles': user_friends_profiles,'user_relationships':user_relationships,
               'all_profiles':all_profiles,'request_received_profiles':request_received_profiles}
    
    return render(request, 'FeedApp/friends.html', context)

        