import format as f
import sensor_detail as sd
import pandas as pd

data = pd.read_csv(r"E:\GEO427\Project\Portland_Air\filter_first_week.csv")# previously cleaned, attaching the name
data = f.trim_frame(data)
form = sd.PurpleAirFormat()
sd.DESTINATION_TIME_ZONE= "America/Vancouver"
clean = f.unchecked_format(data, form)


clean.to_csv(r"E:\GEO427\Project\Portland_Air\filter_first_week_clean.csv")
