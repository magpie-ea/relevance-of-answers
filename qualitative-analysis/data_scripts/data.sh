# create excluded_data.csv and included_data.csv
python3 clean-and-exclude.py
# take included_data.csv and create by_item.csv
python3 group-by-item.py
# take by_item.csv and create by_item_with_stimuli.csv
python3 merge-stimuli.py