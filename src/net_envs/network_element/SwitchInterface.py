import abc


class SwitchInterface(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def forward(self):
        pass
