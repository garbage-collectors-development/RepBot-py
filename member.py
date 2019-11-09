"""This module houses the member class used to manage members once pulled out of
the database."""

from dataclasses import dataclass

@dataclass
class Member:

    id: str
    name: str
    discriminator: str

    def __repr__(self):
        return {'id':self.id,'name':'{0}#{1}'.format(self.name, self.discriminator)}