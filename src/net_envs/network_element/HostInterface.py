import abc


class HostInterface(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def send(self):
        pass
