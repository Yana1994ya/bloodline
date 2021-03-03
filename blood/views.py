from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from blood import models
from blood.fill_request import create_and_fill_mci_request, create_and_fill_single_request
from blood.forms import AcceptDonation, IdSearch, MCIRequestForm, SingleRequestForm


def donation_start(request):
	if request.method == "GET":
		form = IdSearch()
	else:
		form = IdSearch(request.POST)

		if form.is_valid():
			return HttpResponseRedirect(reverse(
				donation_id, kwargs={"id_number": form.cleaned_data["id_number"]}
			))

	return render(request, "donation.html", {"form": form})


def donation_id(request, id_number):
	try:
		patient, initial_data = models.Patient.details(id_number)
	except models.InvalidPatientId:
		return HttpResponseRedirect(reverse(donation_start))

	if request.method == "GET":
		form = AcceptDonation(initial=initial_data)
	else:
		form = AcceptDonation(request.POST, initial=initial_data)

		if form.is_valid():
			data = form.cleaned_data

			patient.update(
				first_name=data["first_name"],
				last_name=data["last_name"],
				birthday=data["birthday"],
				blood_type=data["blood_type"]
			)

			donation = models.Donation(donor=patient, units=data["units"])
			donation.save()

			return HttpResponseRedirect(
				reverse(donation_received, kwargs={"donation_id": donation.id}))

	return render(request, "accept_donation.html", {"form": form, "id_number": id_number})


def donation_received(request, donation_id):
	donation = get_object_or_404(models.Donation, id=donation_id)

	return render(request, "donation_received.html", {"donation": donation})


def single_request_start(request):
	if request.method == "GET":
		form = IdSearch()
	else:
		form = IdSearch(request.POST)

		if form.is_valid():
			return HttpResponseRedirect(reverse(
				single_request_details, kwargs={"id_number": form.cleaned_data["id_number"]}
			))

	return render(request, "single_request_start.html", {"form": form})


def single_request_details(request, id_number):
	try:
		patient, initial_data = models.Patient.details(id_number)
	except models.InvalidPatientId:
		return HttpResponseRedirect(reverse(single_request_start))

	if request.method == "GET":
		form = SingleRequestForm(initial=initial_data)
	else:
		form = SingleRequestForm(request.POST, initial=initial_data)

		if form.is_valid():
			data = form.cleaned_data

			patient.update(
				first_name=data["first_name"],
				last_name=data["last_name"],
				birthday=data["birthday"],
				blood_type=data["blood_type"]
			)

			return HttpResponseRedirect(
				reverse(single_request_confirm, kwargs={
					"id_number": patient.id,
					"units": data["units"]
				}))

	return render(request, "single_request.html", {"form": form, "id_number": id_number})


def single_request_confirm(request, id_number, units):
	units = int(units)
	patient = get_object_or_404(models.Patient, id=id_number)

	if request.method == "GET":
		return render(request, "single_request_confirm.html", {"patient": patient, "units": units})
	else:
		single_request = create_and_fill_single_request(patient, units)

		return HttpResponseRedirect(
			reverse(single_request_complete, kwargs={"request_id": single_request.id}))


def single_request_complete(request, request_id):
	single_request = get_object_or_404(models.SingleRequest, id=request_id)
	return render(request, "single_request_complete.html", {"single_request": single_request})


def mci_request_start(request):
	if request.method == "GET":
		form = MCIRequestForm()
	else:
		form = MCIRequestForm(request.POST)

		if form.is_valid():
			data = form.cleaned_data
			mci_request = create_and_fill_mci_request(data["distribution"].leaf, data["units"])

			return HttpResponseRedirect(reverse(
				mci_request_complete,
				kwargs={"request_id": mci_request.id}
			))

	return render(request, "mci_request.html", {"form": form})


def mci_request_complete(request, request_id: int):
	mci_request = get_object_or_404(models.MCIRequest, id=request_id)
	return render(request, "mci_request_complete.html", {"mci_request": mci_request})
