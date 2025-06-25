from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Salon(models.Model):
    address = models.CharField(max_length=100, verbose_name='Адрес салона')

    def __str__(self):
        return self.address


class Service(models.Model):
    treatment = models.CharField(
        max_length=20,
        verbose_name='Название услуги',
        unique=True
    )
    price = models.DecimalField(
        max_digits=6,
        decimal_places=0,
        verbose_name='Цена'
    )

    def __str__(self):
        return f'{self.treatment} — {self.price} руб.'


class Master(models.Model):
    name = models.CharField(max_length=50, verbose_name='Имя мастера')
    salon = models.ForeignKey(
        Salon,
        verbose_name='Салон',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='masters'
    )
    services = models.ManyToManyField(
        Service,
        verbose_name='Услуги мастера'
    )

    def __str__(self):
        if self.salon:
            return f"{self.name} из «{self.salon.address}»"
        return "Мастер без салона"
 

class Client(models.Model):
    tg_id = models.BigIntegerField(unique=True, verbose_name="Telegram ID")
    name = models.CharField(max_length=50, verbose_name='Имя клиента')
    phonenumber = PhoneNumberField(max_length=12, verbose_name='Номер телефона')

    def __str__(self):
        return self.name


class Registration(models.Model):
    salon = models.ForeignKey(
        Salon,
        verbose_name='Салон',
        on_delete=models.CASCADE
    )
    master = models.ForeignKey(
        Master,
        verbose_name='Мастер',
        on_delete=models.CASCADE
    )
    client = models.ForeignKey(
        Client,
        verbose_name='Клиент',
        on_delete=models.CASCADE
    )
    service = models.ForeignKey(
        Service,
        verbose_name='Услуга',
        on_delete=models.CASCADE
    )
    service_date = models.DateField(
        verbose_name='Дата процедуры'
    )
    slot = models.CharField(
        max_length=13,
        verbose_name='Время записи',
        default=''
    )
    reminder_sent = models.BooleanField(
        default=False,
        verbose_name='Отправилось напоминание'
    )
    registration_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Когда произведена бронь'
    )

    def __str__(self):
        return f"Бронь №{self.pk} на {self.service_date} в {self.slot}"


# Registration.objects.create(
#     salon=salon,
#     master=master,
#     client=client,
#     service=hair,
#     service_date="2025-06-26",
#     slot="10:00-11:00"
# ) Так создаём регистрацию с конкретной услугой мастера


