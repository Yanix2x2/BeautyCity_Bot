from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Salon(models.Model):
    address = models.CharField(max_length=100, verbose_name='Адрес салона')

    def __str__(self):
        return self.address

    class Meta:
        verbose_name = "Салон"
        verbose_name_plural = "Салоны"


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

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"


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

    class Meta:
        verbose_name = "Мастер"
        verbose_name_plural = "Мастера"
 

class Client(models.Model):
    tg_id = models.BigIntegerField(unique=True, verbose_name="Telegram ID")
    name = models.CharField(max_length=50, verbose_name='Имя клиента')
    phonenumber = PhoneNumberField(max_length=12, verbose_name='Номер телефона')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"


class Registration(models.Model):
    TIME_SLOTS = [
        ('09:00', '09:00'),
        ('10:00', '10:00'),
        ('11:00', '11:00'),
        ('12:00', '12:00'),
        ('13:00', '13:00'),
        ('14:00', '14:00'),
        ('15:00', '15:00'),
        ('16:00', '16:00'),
        ('17:00', '17:00'),
    ]
    salon = models.ForeignKey(
        Salon,
        verbose_name='Салон',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    master = models.ForeignKey(
        Master,
        verbose_name='Мастер',
        on_delete=models.CASCADE,
        null=True,
        blank=True
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
        choices=TIME_SLOTS
    )
    reminder_sent = models.BooleanField(
        default=False,
        verbose_name='Отправилось напоминание'
    )
    registration_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Когда произведена запись'
    )

    def __str__(self):
        return f"Запись №{self.pk} на {self.service_date} в {self.slot}"

    class Meta:
        verbose_name = "Запись"
        verbose_name_plural = "Записи"



# Registration.objects.create(
#     salon=salon,
#     master=master,
#     client=client,
#     service=hair,
#     service_date="2025-06-26",
#     slot="10:00-11:00"
# ) Так создаём регистрацию с конкретной услугой мастера
