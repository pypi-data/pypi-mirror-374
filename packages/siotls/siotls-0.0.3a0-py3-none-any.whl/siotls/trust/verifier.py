import abc


class X509Verifier(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def verify_chain(self, conn, entry_chain):
        raise NotImplementedError
