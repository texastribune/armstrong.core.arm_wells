import datetime
from django.db import models


class WellManager(models.Manager):
    def get_current(self, title=None, titles=[], slug=None):
        now = datetime.datetime.now()
        filter_params = dict(pub_date__lte=now, active=True)

        if titles:
            filter_params['type__title__in'] = titles
            results = (self.filter(**filter_params)
                           .select_related('type')
                           .exclude(expires__lte=now, expires__isnull=False)
                           .order_by('type', '-pub_date')
                           .distinct('type'))

            return {well.type.title: well for well in results}

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
