"""
Open and close time calculations
for ACP-sanctioned brevets
following rules described at https://rusa.org/octime_alg.html
and https://rusa.org/pages/rulesForRiders
"""
import arrow

#  Note for CIS 322 Fall 2016:
#  You MUST provide the following two functions
#  with these signatures, so that I can write
#  automated tests for grading.  You must keep
#  these signatures even if you don't use all the
#  same arguments.  Arguments are explained in the
#  javadoc comments.
#


def open_time(control_dist_km, brevet_dist_km, brevet_start_time):
    """
    Args:
       control_dist_km:  number, the control distance in kilometers
       brevet_dist_km: number, the nominal distance of the brevet
           in kilometers, which must be one of 200, 300, 400, 600,
           or 1000 (the only official ACP brevet distances)
       brevet_start_time:  An ISO 8601 format date-time string indicating
           the official start time of the brevet
    Returns:
       An ISO 8601 format date string indicating the control open time.
       This will be in the same time zone as the brevet start time.
    """
    print("**************End: ", brevet_dist_km)
    start = arrow.get(brevet_start_time)
    #start = brevet_start_time
    #print(type(start))
    #print("*******************\nStart: ", start)
    open_table = [(1000, 28), (600, 30), (400, 32), (200, 34)]
    remaining_dist = control_dist_km
    open_delay = 0
    i = 0

    for pair in open_table:
        dist, max_speed = pair

        if control_dist_km == 0:
            open_delay = 0
            break

        try:
            next_dist, next_max_speed = open_table[i+1]
        except:
            next_dist = 0  # prevent list index out of range errors

        if (control_dist_km <= (brevet_dist_km*1.2)) and (brevet_dist_km == dist) and (control_dist_km > brevet_dist_km):  # Total brevel distance can be 20% above the bound
            working_dist = dist - next_dist
            open_delay += (working_dist / max_speed)
            remaining_dist = next_dist

        elif (remaining_dist <= dist) and (remaining_dist > next_dist) and not (control_dist_km > brevet_dist_km):
            working_dist = remaining_dist - next_dist
            open_delay += (working_dist / max_speed)
            remaining_dist = next_dist

        i +=1

    delay_hours = int(open_delay)
    delay_mins = (open_delay - delay_hours) * 60
    int_delay_mins = int(delay_mins)

    if (delay_mins - int_delay_mins) >= .5:
        delay_mins = int_delay_mins + 1  # Handle rounding up
    else:
        delay_mins = int_delay_mins

    open_time = start.shift(hours=+delay_hours, minutes=+delay_mins)
    return open_time.isoformat()

    #return arrow.now().isoformat()


def close_time(control_dist_km, brevet_dist_km, brevet_start_time):
    """
    Args:
       control_dist_km:  number, the control distance in kilometers
          brevet_dist_km: number, the nominal distance of the brevet
          in kilometers, which must be one of 200, 300, 400, 600, or 1000
          (the only official ACP brevet distances)
       brevet_start_time:  An ISO 8601 format date-time string indicating
           the official start time of the brevet
    Returns:
       An ISO 8601 format date string indicating the control close time.
       This will be in the same time zone as the brevet start time.
    """

    start = arrow.get(brevet_start_time)
    close_table = [(1000, 11.428), (600, 15), (400, 15), (200, 15)]
    close_brevet = [(1000, 75), (600, 40), (400, 27), (300, 20), (200, 13.5)]
    remaining_dist = control_dist_km
    close_delay = 0
    i = 0

    if control_dist_km >= brevet_dist_km:  # deal with special cases for the finish
        for pair in close_brevet:
            dist, time = pair

            try:
                next_dist, next_time = close_brevet[i+1]
            except:
                next_dist = 0

            if (brevet_dist_km <= (dist + (dist*.2))) and (brevet_dist_km > next_dist):
                close_delay = time
            i += 1

        delay_hours = int(close_delay)
        delay_mins = (close_delay - delay_hours) * 60
        int_delay_mins = int(delay_mins)

        if (delay_mins - int_delay_mins) >= .5:
            delay_mins = int_delay_mins + 1  # Handle rounding up
        else:
            delay_mins = int_delay_mins

        close_time = start.shift(hours=+delay_hours, minutes=+delay_mins)
        return close_time.isoformat()

    for pair in close_table:
        dist, max_speed = pair

        if control_dist_km == 0:
            close_delay = 1  # The start point stays open for 1 hour
            break

        try:
            next_dist, next_max_speed = close_table[i+1]
        except:
            next_dist = 0

        if (remaining_dist <= dist) and (remaining_dist > next_dist):
            working_dist = remaining_dist - next_dist
            close_delay += (working_dist / max_speed)
            remaining_dist = next_dist

        i += 1


    delay_hours = int(close_delay)
    delay_mins = (close_delay - delay_hours) * 60
    int_delay_mins = int(delay_mins)

    if (delay_mins - int_delay_mins) >= .5:
        delay_mins = int_delay_mins + 1  # Handle rounding up
    else:
        delay_mins = int_delay_mins

    close_time = start.shift(hours=+delay_hours, minutes=+delay_mins)
    return close_time.isoformat()

    #return arrow.now().isoformat()
