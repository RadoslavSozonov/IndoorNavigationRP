interval = 0.1
sample_rate = 44100
chirp_amount = 500
recognize_chirp_amount = 10
# amount of chirps that are ignored, since some of the last chirps dont work
chirp_last_error = 5
chirp_first_error = 5
good_chirp_amount = chirp_amount - chirp_last_error - chirp_first_error
chirp_radius = 0.016

interval_samples = sample_rate * interval
chirp_radius_samples = int(sample_rate * chirp_radius/2)


min_frequency = 19500
max_frequency = 20500
