import requests
import gtfs_realtime_pb2



FEED_URL = 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-g'

# Fetch the data
response = requests.get(FEED_URL)

feed = gtfs_realtime_pb2.FeedMessage()
feed.ParseFromString(response.content)

import time

station_id = 'G35N'  # Replace with your station stop ID
upcoming_trains = []

for entity in feed.entity:
    if not entity.HasField('trip_update'):
        continue

    for stu in entity.trip_update.stop_time_update:
        if stu.stop_id == station_id:
            arrival_time = None
            if stu.HasField('arrival') and stu.arrival.HasField('time'):
                arrival_time = stu.arrival.time
            if stu.HasField('departure') and stu.departure.HasField('time'):
                arrival_time = stu.departure.time

            if arrival_time:
                upcoming_trains.append({
                    'trip_id': entity.trip_update.trip.trip_id,
                    'route_id': entity.trip_update.trip.route_id,
                    'arrival_time': arrival_time
                })

# Sort by arrival time
upcoming_trains.sort(key=lambda x: x['arrival_time'])

# Print upcoming times
for train in upcoming_trains:
    print(f"Route {train['route_id']} - Arriving at {time.strftime('%I:%M:%S %p', time.localtime(train['arrival_time']))}")

