from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.conf import settings
import json
from pytube import YouTube
import os
import assemblyai as aai
import openai
from .models import BlogPost


@login_required
def index(request):
    return render(request, 'index.html')

@csrf_exempt
def generate_blog(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            yt_link = data['link']
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid data sent'}, status=400)


        # get yt title
        title = yt_title(yt_link)

        # get transcript
        transcription = get_transcription(yt_link)
        if not transcription:
            return JsonResponse({'error': " Failed to get transcript"}, status=500)


        # use OpenAI to generate the blog
        blog_content = generate_blog_from_transcription(transcription)
        if not blog_content:
            return JsonResponse({'error': " Failed to generate blog article"}, status=500)

        # save blog article to database
        new_blog_article = BlogPost.objects.create(
            user=request.user,
            youtube_title=title,
            youtube_link=yt_link,
            generated_content=blog_content,
        )
        new_blog_article.save()

        # return blog article as a response
        return JsonResponse({'content': blog_content})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

def yt_title(link):
    # yt = YouTube(link)
    title = "Hello all....Prathap here, "
    return title

def download_audio(link):
    yt = YouTube(link)
    video = yt.streams.filter(only_audio=True).first()
    out_file = video.download(output_path=settings.MEDIA_ROOT)
    base, ext = os.path.splitext(out_file)
    new_file = base + '.mp3'
    os.rename(out_file, new_file)
    return new_file

def get_transcription(link):
    # audio_file = download_audio(link)
    # aai.settings.api_key = "199d5bad45610da38"

    # transcriber = aai.Transcriber()
    # transcript = transcriber.transcribe(audio_file)

    return "Hello all------------"

def generate_blog_from_transcription(transcription):
    # openai.api_key = "HHyenJ9T_4xjHiWzSnHBNT3BlbkFJc8e6Xk25KVOMPsqMT0ntnxY19gMkccgWrknErg7uHzJ7-iC8ykHMv6JVPnWehfNkHAI1dnvesA"

    # prompt = f"Based on the following transcript from a YouTube video, write a comprehensive blog article, write it based on the transcript, but dont make it look like a youtube video, make it look like a proper blog article:\n\n{transcription}\n\nArticle:"

    # response = openai.Completion.create(
    #     model="text-davinci-003",
    #     prompt=prompt,
    #     max_tokens=1000
    # )

    generated_content = "David I'm David Curley at the Smithsonian Air and Space Museum where we are marking 50 years since man landed and walked on the moon in a lander just like this one. We are going to show you some of the actual ABC news coverage from 50 years ago during that eight day mission of this remarkable achievement. Apollo 11's lander, the Eagle, would be the first manned craft to land on the moon. For training, NASA came up with an unusual contraption. Neil Armstrong actually had to eject from it once and then he had a couple of successful flights. ABC News anchor At the time 50 years ago, Frank Reynolds, with a look at that unusual trainer. Apollo 11 commander Neil Armstrong is at the controls of a lunar landing training vehicle, testing the reaction control jets. These thrusters stabilize the LEM during landing and takeoff. The LLTV is designed to simulate the behavior of the LM as it lands in the moon's gravity. Lunar gravity is one sixth that of the Earth's. Neil Armstrong flew one of these vehicles on May 6, 1968, and that flight was nearly his last. Later reports by a NASA investigating team said the crash, which we'll see soon, was caused by a loss of fuel pressure compounded by a warning light that failed to work. Armstrong's coolness under pressure saved himself and possibly months of delay for the Apollo program. Later that same year, 1968, another test pilot, Joseph Alegrandi, also escaped from an LLTV just before it crashed. The training vehicle then underwent several design modifications and improvements. Engineers had to increase the vehicle's rocket power to help stabilize the craft. That made the LLTV less of a moon gravity simulator, but it improved pilot safety. On June 16, 1969, Neil Armstrong flew the vehicle, sometimes called the flying bedstead, to several perfect landings. The question was, how does the machine fly? And the answer is that we're very pleased with the way it flies. It's a significant improvement over the LLRV which we were flying here a year ago. And I think it does an excellent job of actually capturing the handling characteristics of the lunar module in a landing maneuver. It's really a great deal different than any other kind of aircraft that I've ever flown. The simulation of lunar gravity has some aspects that make this type of flight sufficiently different from anything else we've ever done to make this vehicle very worthwhile. And I'm very pleased that I've had the opportunity to get some flights in it here. Just before the Apollo 11 flight,"

    return generated_content



def blog_list(request):
    blog_articles = BlogPost.objects.filter(user=request.user)
    return render(request, "all-blogs.html", {'blog_articles': blog_articles})

def blog_details(request, pk):
    blog_article_detail = BlogPost.objects.get(id=pk)
    if request.user == blog_article_detail.user:
        return render(request, 'blog-details.html', {'blog_article_detail': blog_article_detail})
    else:
        return redirect('/')


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            error_message = 'Invalid username or password'
            return render(request, 'login.html', {'error_message': error_message})

    return render(request, 'login.html')

def user_signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        password = request.POST['password']
        repeatPassword = request.POST['repeatPassword']

        if password == repeatPassword:
            try:
                user = User.objects.create_user(username, email, password)
                user.save()
                login(request, user)
                return redirect('/')
            except:
                error_message = "Error creating account"
                return render(request, 'signup.html', {'error_message': error_message})
        else:
            error_message = 'Password do not match'
            return render(request, 'signup.html', {'error_message': error_message})

    return render(request, 'signup.html')

def user_logout(request):
    logout(request)
    return redirect('/')