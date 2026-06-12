from models.filter import Filter
import time

filter_obj = Filter()

for i in range(20):

    filter_obj.update()

    print(filter_obj.get_filter_data())

    time.sleep(1)

    filter_obj.replace_filter()

print(filter_obj.get_filter_data())