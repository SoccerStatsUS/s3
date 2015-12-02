import pymongo

from places.models import Country, State, City

connection = pymongo.Connection()
soccer_db = connection.soccer



def make_city_pre_getter():
    """
    Dissassemble a location string into city, state, and country pieces.
    City, state, and country are all optional, although country should (always?) 
    exist.
    e.g. Dallas, Texas -> {'name': 'Dallas', 'state': 'Texas', 'country': 'United States' }
    Cape Verde -> {'name': '', 'city': '', 'country': 'United States',
    """
    # Would like to add neighborhood to this.
    # Should this be part of normalize instead of here? Possibly.

    def make_state_abbreviation_dict():
        # Map abbreviation to state name, state country.
        d = {}
        for e in soccer_db.states.find():
            d[e['abbreviation']] = (e['name'], e.get('country'))

        return d


    def make_state_name_dict():
        d = {}
        for e in soccer_db.states.find():
            d[e['name']] = (e['name'], e.get('country'))

        return d

        

    country_name_set = set([e['name'].strip() for e in soccer_db.countries.find()])
    state_abbreviation_dict = make_state_abbreviation_dict()
    state_name_dict = make_state_name_dict()


    def get_dict(s):

        state = country = None

        if ',' in s:
            pieces = s.split(',')
            end = pieces[-1].strip()

            if end in state_abbreviation_dict:
                state, country = state_abbreviation_dict[end]

            elif end in state_name_dict:
                state, country = state_name_dict[end]

            elif end in country_name_set:
                country = end

        if country or state:
            name = ','.join(pieces[:-1])
        else:
            name = s

        # Change name to city.
        return {
            'name': name,
            'state': state,
            'country': country,
            }


    return get_dict



def make_city_getter():
    """
    
    """

    cg = make_city_pre_getter()
    
    def get_city(s):
        c = cg(s)

        state = country = None
        if c['state']:
            state = State.objects.get(name=c['state'])

        if c['country']:
            country = Country.objects.get(name=c['country'])
        
        try:
            return City.objects.get(name=c['name'], state=state, country=country)
        except:
            return City.objects.create(name=c['name'], state=state, country=country)

    return get_city
