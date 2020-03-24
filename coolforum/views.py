from django.shortcuts import render, redirect

# add to your views
def index(request):
    return render(request, 'index.html')

def privacy(request):
	return render(request, 'privacy.html')