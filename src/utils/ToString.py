import jsonpickle


class ToString(object):

    def __repr__(self):
        return jsonpickle.encode(self)

    def __str__(self):
        return jsonpickle.encode(self)
