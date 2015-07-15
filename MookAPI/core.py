from flask.ext.mongoengine import MongoEngine

db = MongoEngine()


class Service(object):

    __model__ = None

    def _isinstance(self, model, raise_error=False):

        rv = isinstance(model, self.__model__)

        if not rv and raise_error:
            raise ValueError('%s is not of type %s' % (model, self.__model__))

        return rv

    def _preprocess_params(self, kwargs):
        kwargs.pop('csrf_token', None)
        return kwargs

    def save(self, model):
        self._isinstance(model)
        model.save(validate=False, clean=True)  # FIXME Temporary hack due to a bug in MongoEngine.
        return model

    def queryset(self):
        return self.__model__.objects

    def all(self):
        return self.queryset().all()

    def get(self, id=None, **kwargs):
        if id:
            return self.queryset().get(id=id)
        else:
            return self.queryset().get(**kwargs)

    def get_all(self, *ids):
        return self.queryset().filter(id__in=ids).all()

    def find(self, **kwargs):
        return self.queryset().filter(**kwargs)

    def first(self, **kwargs):
        return self.find(**kwargs).first()

    def get_or_404(self, id=None, **kwargs):
        if id:
            return self.queryset().get_or_404(id=id)
        else:
            return self.queryset().get_or_404(**kwargs)

    def new(self, **kwargs):
        return self.__model__(**self._preprocess_params(kwargs))

    def create(self, **kwargs):
        return self.save(self.new(**kwargs))

    def update(self, model, **kwargs):
        self._isinstance(model)
        for k, v in self._preprocess_params(kwargs).items():
            setattr(model, k, v)
        self.save(model)
        return model

    def delete(self, model):
        self._isinstance(model)
        model.delete()
