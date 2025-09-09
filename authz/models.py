from django.db import models
from core.models import TimeStampedModel

class Rol(TimeStampedModel):
    nombre = models.CharField(max_length=50, unique=True)
    def __str__(self): return self.nombre

class Usuario(TimeStampedModel):
    ESTADOS = (("ACTIVO","ACTIVO"),("INACTIVO","INACTIVO"),("BLOQUEADO","BLOQUEADO"))
    GENEROS = (("M","Masculino"), ("F","Femenino"), ("O","Otro"), ("N","Prefiero no decir"))
    
    nombres = models.CharField(max_length=100, help_text="Nombres del usuario")
    apellidos = models.CharField(max_length=100, help_text="Apellidos del usuario")
    email = models.EmailField(max_length=191, unique=True)
    password_hash = models.CharField(max_length=255)
    telefono = models.CharField(max_length=25, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True, help_text="Fecha de nacimiento")
    genero = models.CharField(max_length=1, choices=GENEROS, blank=True, null=True)
    documento_identidad = models.CharField(max_length=20, blank=True, null=True, help_text="Cédula de identidad o pasaporte")
    pais = models.CharField(max_length=50, blank=True, null=True, help_text="País de residencia")
    ciudad = models.CharField(max_length=50, blank=True, null=True, help_text="Ciudad de residencia")
    estado = models.CharField(max_length=10, choices=ESTADOS, default="ACTIVO")
    roles = models.ManyToManyField(Rol, through="RolUsuario", related_name="usuarios")
    
    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}".strip()
    
    def __str__(self): return f"{self.nombre_completo} <{self.email}>"

class RolUsuario(models.Model):
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    class Meta:
        unique_together = (("rol","usuario"),)
