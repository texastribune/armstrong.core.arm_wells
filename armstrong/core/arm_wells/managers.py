import datetime
import time
from django.db import models


class WellManager(models.Manager):
    def get_current(self, title=None, titles=[], slug=None):
        start_time = time.time()
        now = datetime.datetime.now()
        filter_params = dict(pub_date__lte=now, active=True)

        if titles:
            titles_dict = {}
            filter_params['type__title__in'] = titles
            results = (self.filter(**filter_params)
                           .exclude(expires__lte=now, expires__isnull=False))
            for title in titles:
                titles_dict.update({'title': title, 'well': results.filter(type__title=title).latest('pub_date')})

            end_time = time.time()
            how_much_time = end_time - start_time
            print(f'Took {how_much_time} to finish')
            return titles_dict

        if (title):
            filter_params['type__title'] = title
        elif (slug):
            filter_params['type__slug'] = slug
        else:
            raise self.model.DoesNotExist()
        
        result = (self.filter(**filter_params)
                    .exclude(expires__lte=now, expires__isnull=False)
                    .latest('pub_date'))

        end_time = time.time()
        how_much_time = end_time - start_time
        print(f'Took {how_much_time} to finish')

        return result
