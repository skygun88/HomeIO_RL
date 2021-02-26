from os import stat
import random
import time

def working_feedback(states, all_devices):
    l1_idx, l2_idx, r_idx, h_idx, rb_idx, rt_idx, ot_idx, ob_idx = 0, 1, 2, 3, 4, 5, 6, 7

    action_cnt = [0]*4
    ''' --- Feedback on Brightness --- '''
    while states[rb_idx] < 5.0:
        if states[ob_idx] < 1.0: # Evening or Night
            light_idxs = [l1_idx, l2_idx]
            random.shuffle(light_idxs)
            if all_devices[light_idxs[0]].state() != 10.0:
                all_devices[light_idxs[0]].actuate(1)
                action_cnt[light_idxs[0]] += 1
            else:
                if all_devices[light_idxs[1]].state() != 10.0:
                    all_devices[light_idxs[1]].actuate(1)
                    action_cnt[light_idxs[1]] += 1
        else: # Morning or Afternoon
            if all_devices[r_idx].state() < 10.0:
                all_devices[r_idx].up()
                action_cnt[r_idx] += 1
            else:
                light_idxs = [l1_idx, l2_idx]
                random.shuffle(light_idxs)
                if all_devices[light_idxs[0]].state() != 10.0:
                    all_devices[light_idxs[0]].actuate(1)
                    action_cnt[light_idxs[0]] += 1
                else:
                    if all_devices[light_idxs[1]].state() != 10.0:
                        all_devices[light_idxs[1]].actuate(1)
                        action_cnt[light_idxs[1]] += 1
        time.sleep(0.1)
        states = list(map(lambda x: x.state(), all_devices))

    ''' --- Feedback on Temperature --- '''
    while states[rt_idx] < 15 or states[rt_idx] > 20:
        if states[rt_idx] < 15: # Cool state
            if states[ot_idx] < states[rt_idx]: # if outside is lower than room
                if all_devices[h_idx].state() > 8.0:
                    break
                else:
                    all_devices[h_idx].power_up()
                    action_cnt[h_idx] += 1
            else: # if outside is higher than room
                if states[ot_idx] < 15:
                    if all_devices[h_idx].state() > 7.0:
                        break
                    else:
                        all_devices[h_idx].power_up()
                        action_cnt[h_idx] += 1

        elif states[rt_idx] > 20: # Hot state
            if states[ot_idx] < states[rt_idx]: # if outside is lower than room
                if all_devices[h_idx].state() < 3.0:
                    break
                else:
                    all_devices[h_idx].power_down()
                    action_cnt[h_idx] += 1
            else: # if outside is higher than room
                if all_devices[h_idx].state() == 0.0:
                    break
                else:
                    all_devices[h_idx].power_down()
                    action_cnt[h_idx] += 1
            
        time.sleep(0.1)
        states = list(map(lambda x: x.state(), all_devices))

    final_state = list(map(lambda x: x.state(), all_devices))
    return action_cnt, final_state





                
