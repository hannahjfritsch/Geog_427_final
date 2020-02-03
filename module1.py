import format as f
import sensor_detail as sd
import pandas as pd

data = pd.read_csv(r"C:\Users\Hannah Fritsch\Documents\DEMP_Code\Download\full_merge.csv"
)# previously cleaned, attaching the name
data = f.trim_frame(data)
form = sd.PurpleAirFormat()
sd.DESTINATION_TIME_ZONE= "America/Vancouver"
clean = f.unchecked_format(data, form)


clean.to_csv(r"C:\Users\Hannah Fritsch\Documents\DEMP_Code\Download\clean_merge.csv")
