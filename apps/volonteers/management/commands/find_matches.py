from django.core.management.base import BaseCommand
from apps.db_users.models import ContactForm
from django.db import transaction
from django.core.paginator import Paginator
from pytorch_forecasting import TemporalFusionTransformer, TimeSeriesDataSet
from pytorch_forecasting.data import NaNLabelEncoder
import torch
import pandas as pd 
class Command(BaseCommand):
    help = 'Find matches between seekers and volunteers based on availability using AI.'

    def handle(self, *args, **kwargs):
        seeker_batch_size = 100
        volunteer_batch_size = 500

        # Query for seekers and volunteers
        seekers = ContactForm.objects.filter(is_volunteer=False, buddy_id__isnull=True)
        volunteers = ContactForm.objects.filter(is_volunteer=True, buddy_id__isnull=True)

        seeker_paginator = Paginator(seekers, seeker_batch_size)
        volunteer_paginator = Paginator(volunteers, volunteer_batch_size)

        # Train the TFT model once at the start
        self.stdout.write("Training the model for availability matching...")
        tft_model = train_tft_model(seekers, volunteers)
        self.stdout.write("Model training completed.")

        for seeker_page_num in seeker_paginator.page_range:
            seeker_page = seeker_paginator.page(seeker_page_num)
            for volunteer_page_num in volunteer_paginator.page_range:
                volunteer_page = volunteer_paginator.page(volunteer_page_num)

                # Use the trained model to find matches
                matches = find_matches_with_info(seeker_page, volunteer_page, tft_model)

                for match in matches:
                    seeker_info = match['seeker']
                    volunteer_info = match['volunteer']

                    # Log the match
                    self.stdout.write(
                        f"Seeker {seeker_info['name']} matched with Volunteer {volunteer_info['name']}."
                    )

                    # Update buddy_id in the database
                    try:
                        seeker = ContactForm.objects.get(id=seeker_info['id'])
                        volunteer = ContactForm.objects.get(id=volunteer_info['id'])

                        if not seeker.buddy_id and not volunteer.buddy_id:
                            with transaction.atomic():
                                seeker.buddy_id = str(volunteer.id)
                                volunteer.buddy_id = str(seeker.id)
                                seeker.save()
                                volunteer.save()
                    except ContactForm.DoesNotExist:
                        self.stdout.write(f"Error: Seeker or Volunteer with given ID not found.")


# Example data preprocessing function to train the model

def train_tft_model(seekers, volunteers):
    # Example preprocessing of availability data for both seekers and volunteers
    seeker_vectors = [availability_vector(seeker) for seeker in seekers]
    volunteer_vectors = [availability_vector(volunteer) for volunteer in volunteers]

    # Create a combined dataset of seekers and volunteers
    dataset = seeker_vectors + volunteer_vectors
    labels = [1] * len(seeker_vectors) + [0] * len(volunteer_vectors)  # 1 for seeker, 0 for volunteer

    # Create unique group IDs using seeker and volunteer IDs
    seeker_ids = [seeker.id for seeker in seekers]
    volunteer_ids = [volunteer.id for volunteer in volunteers]
    group_ids = seeker_ids + volunteer_ids  # Each user's ID as the group ID

    # Create a time index (assuming each instance represents a unique time step)
    time_idx = list(range(len(dataset)))

    # Create the dataset with group IDs and time index
    data = pd.DataFrame({
        'availability_vector': dataset,
        'time_idx': time_idx,
        'group_id': group_ids,
        'label': labels
    })

    # Converting the dataset into a TimeSeriesDataSet
    ts_dataset = TimeSeriesDataSet(
        data,
        time_idx="time_idx",
        target="label",  # The target column
        group_ids=["group_id"],  # Grouping based on unique user IDs
        max_encoder_length=10,  # Look-back window
        max_prediction_length=1,  # Single prediction step
        static_categoricals=["group_id"],
        time_varying_known_reals=["availability_vector"],  # Use availability vectors as features
        target_normalizer=NaNLabelEncoder(),
    )

    # Split dataset into train and validation
    train_data, val_data = ts_dataset.split_by_time()

    # Define the Temporal Fusion Transformer (TFT) model
    tft = TemporalFusionTransformer.from_dataset(
        train_data,
        learning_rate=0.03,
        hidden_size=16,  # Number of hidden units
        attention_head_size=1,
        dropout=0.1,
        hidden_continuous_size=8,
        output_size=1,  # Predicting match success
        loss=torch.nn.MSELoss(),
    )

    # Train the model
    tft_trainer = torch.optim.Adam(tft.parameters(), lr=0.03)
    tft_trainer.fit(train_data, val_data, max_epochs=10)

    return tft
def find_matches_with_info(seekers, volunteers, trained_model):
    matches = []

    for seeker in seekers:
        seeker_vector = availability_vector(seeker)

        for volunteer in volunteers:
            volunteer_vector = availability_vector(volunteer)

            # Combine the features into a dataset for prediction
            feature_vector = seeker_vector + volunteer_vector  # Concatenate availability features

            # Predict match probability using the trained TFT model
            match_prob = trained_model.predict(feature_vector)

            if match_prob > 0.8:  # Threshold for successful matching
                match_data = {
                    "seeker": {
                        "id": seeker.id,
                        "name": f"{seeker.first_name} {seeker.last_name}",
                        "phone": seeker.phone,
                        "email": seeker.email,
                        "address": seeker.address
                    },
                    "volunteer": {
                        "id": volunteer.id,
                        "name": f"{volunteer.first_name} {volunteer.last_name}",
                        "phone": volunteer.phone,
                        "email": volunteer.email,
                        "address": volunteer.address
                    }
                }
                matches.append(match_data)
                break  # Exit once a match is found for this seeker

    return matches


def availability_vector(contact_form):
    availability = {
        'monday': [contact_form.monday_morning, contact_form.monday_afternoon, contact_form.monday_evening],
        'tuesday': [contact_form.tuesday_morning, contact_form.tuesday_afternoon, contact_form.tuesday_evening],
        'wednesday': [contact_form.wednesday_morning, contact_form.wednesday_afternoon, contact_form.wednesday_evening],
        'thursday': [contact_form.thursday_morning, contact_form.thursday_afternoon, contact_form.thursday_evening],
        'friday': [contact_form.friday_morning, contact_form.friday_afternoon, contact_form.friday_evening],
        'saturday': [contact_form.saturday_morning, contact_form.saturday_afternoon, contact_form.saturday_evening],
        'sunday': [contact_form.sunday_morning, contact_form.sunday_afternoon, contact_form.sunday_evening],
    }
    vector = []
    for day in availability:
        for slot in availability[day]:
            vector.append(int(slot))  # 1 for available, 0 for unavailable
    return vector


def match_availability(seeker, volunteer):
    # Check if the seeker and volunteer's availability dates overlap
    if seeker.start_date > volunteer.end_date or volunteer.start_date > seeker.end_date:
        return False

    # Calculate overlapping date range
    overlap_start = max(seeker.start_date, volunteer.start_date)
    overlap_end = min(seeker.end_date, volunteer.end_date)

    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    time_slots = ['all_day', 'morning', 'afternoon', 'evening']

    for day in days:
        seeker_available_on_day = any(getattr(seeker, f"{day}_{slot}") for slot in time_slots)
        volunteer_available_on_day = any(getattr(volunteer, f"{day}_{slot}") for slot in time_slots)

        if seeker_available_on_day and volunteer_available_on_day:
            for slot in time_slots:
                seeker_available = getattr(seeker, f"{day}_{slot}")
                volunteer_available = getattr(volunteer, f"{day}_{slot}")

                if seeker_available and volunteer_available:
                    print(f"Match found on {day} {slot} between {seeker.first_name} and {volunteer.first_name}")
                    return True

    return False