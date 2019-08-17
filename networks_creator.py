import glm
import itertools

def is_capacitor_excluded(capacitorName):
    return capacitorName in EXCLUDED

def extract_all_capacitors_from_network(network):
    capacitors = {}
    for object in network.get('objects'):
        if (isCapacitor(object)):
            if (not is_capacitor_excluded(object['attributes']['name'])):
                capacitors[object['attributes']['name']] = dict(object)
    remove_all_capacitors_from_network(network)
    return capacitors

def update_networks_capacitors(network, capacitors):
    for object in network:
        if (isCapacitor(object)):
            object['attributes'] = capacitors[object['attributes']['name']]


def isCapacitor(object):
    return object['name'] == 'capacitor'

def generate_all_possible_options_for_capacity(capacitors):
    allOptionsForWorkingCapacitors = []
    for L in range(0, len(capacitors.keys()) + 1):
        for subset in itertools.combinations(capacitors.keys(), L):
            allOptionsForWorkingCapacitors.append(list(subset))
    return allOptionsForWorkingCapacitors

def remove_all_capacitors_from_network(network):
    objects = [object for object in network.get('objects') if
               object['name'] != 'capacitor' or is_capacitor_excluded(object['attributes']['name'])]
    network['objects'] = objects

# all options -> an option contains names of capacitors to be turned on together
def create_network_for_each_capacitor_setup(noCapacitorNetwork, allOptionsForCapacitors, capacitors):
    networkIndex = 0
    network = noCapacitorNetwork
    for option in allOptionsForCapacitors:
        for capacitor in option:
            network.get('objects').insert(0, capacitors[capacitor])
        glm.dump(network, "networks/network_" + str(networkIndex) + ".glm")
        remove_all_capacitors_from_network(network)
        networkIndex += 1

#creates all files possible with given capacitors
def create(networkFile, excludedCapacitors):
    global EXCLUDED
    EXCLUDED = excludedCapacitors
    network = glm.load(networkFile)
    capacitors = extract_all_capacitors_from_network(network)
    allOptionsForWorkingCapacitors = generate_all_possible_options_for_capacity(capacitors)
    create_network_for_each_capacitor_setup(network, allOptionsForWorkingCapacitors, capacitors)

# if __name__ == '__main__':
#     create("IEEE8500_ALL_ON_NETWORK.glm", ['cap_capbank0b', 'cap_capbank2b'])
