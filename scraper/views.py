from django.shortcuts import render
from django import forms
from django.template import loader
from .scraper import run_scraper
# Create your views here.

class FlightForm(forms.Form):
    origin = forms.CharField(label="Origin", max_length=100)
    destination = forms.CharField(label="Destination", max_length=100)
    departure_date = forms.DateField(
        label="Departure Date",
        widget=forms.DateInput(attrs={'type': 'date'})
    )


def form_view(request):
    result = None
    if request.method == "POST":
        form = FlightForm(request.POST)
        if form.is_valid():
            # You can process the data here
            result = form.cleaned_data  # For demonstration
            run_scraper(result["departure_date"].strftime("%Y-%m-%d"))
    else:
        form = FlightForm()
    return render(request, 'form.html', {'form': form, 'result': result})