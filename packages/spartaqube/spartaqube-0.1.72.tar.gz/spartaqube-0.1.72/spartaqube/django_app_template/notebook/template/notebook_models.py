from django.db import models


class QubeModel(models.Model):


    class Meta:
        abstract = True
        app_label = 'qube'


class ExampleModelToken(QubeModel):
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10)
    price_usd = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f'{self.name} ({self.symbol}): ${self.price_usd}'

#END OF QUBE
