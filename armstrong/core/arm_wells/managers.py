import datetime
from django.db import models


class WellManager(models.Manager):
    def get_current(self, title=None, titles=[], slug=None):
        now = datetime.datetime.now()
        filter_params = dict(pub_date__lte=now, active=True)

        if titles:
            titles_dict = {}
            filter_params['type__title__in'] = titles
            results = (self.filter(**filter_params)
                           .select_related('type')
                           .exclude(expires__lte=now, expires__isnull=False))
            for title in titles:
                titles_dict.update({title: results.filter(type__title=title).latest('pub_date')})

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

        return result
