# core/management/commands/seed_zonas_trabajo.py
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import ZonaTrabajo

class Command(BaseCommand):
    help = "Siembra datos iniciales para zonas de trabajo"

    def handle(self, *args, **options):
        with transaction.atomic():
            zonas_data = [
                {
                    "nombre": "Oficina Central - Piso 2",
                    "area": "Administración - RRHH",
                    "ubicacion": "Edificio Principal, Piso 2, Ala Norte",
                    "supervisor": "Dirección General",
                    "notas": "Reunión semanal con jefaturas de área (miércoles 12:00)."
                },
                {
                    "nombre": "Sala de Reuniones - Piso 1",
                    "area": "Administración General",
                    "ubicacion": "Edificio Principal, Piso 1, Recepción",
                    "supervisor": "Gerencia Administrativa",
                    "notas": "Reserva previa requerida. Capacidad máxima 12 personas."
                },
                {
                    "nombre": "Área de Capacitación",
                    "area": "Desarrollo y Capacitación",
                    "ubicacion": "Edificio Anexo, Piso 1",
                    "supervisor": "Jefatura Capacitación",
                    "notas": "Disponible para talleres y capacitaciones internas. Horario: Lunes a Viernes 8:00-18:00."
                },
                {
                    "nombre": "Oficina Contabilidad",
                    "area": "Finanzas y Contabilidad",
                    "ubicacion": "Edificio Principal, Piso 2, Ala Sur",
                    "supervisor": "Gerencia Financiera",
                    "notas": "Acceso restringido. Archivo documentación financiera."
                },
                {
                    "nombre": "Sala de Descanso",
                    "area": "Bienestar Laboral",
                    "ubicacion": "Edificio Principal, Piso 1, Zona Común",
                    "supervisor": "Jefatura RRHH",
                    "notas": "Espacio recreativo. Uso exclusivo empleados. Horario continuo."
                },
                {
                    "nombre": "Centro de Operaciones TI",
                    "area": "Tecnologías de la Información",
                    "ubicacion": "Edificio Servidores, Sótano",
                    "supervisor": "Jefatura TI",
                    "notas": "Acceso con autorización. Monitoreo 24/7 sistemas corporativos."
                },
                {
                    "nombre": "Oficina Ventas",
                    "area": "Comercial y Ventas",
                    "ubicacion": "Edificio Principal, Piso 3",
                    "supervisor": "Gerencia Comercial",
                    "notas": "Área abierta para equipo comercial. Reuniones diarias 9:00 AM."
                },
                {
                    "nombre": "Laboratorio Desarrollo",
                    "area": "Investigación y Desarrollo",
                    "ubicacion": "Edificio Innovación, Piso 2",
                    "supervisor": "Jefatura I+D",
                    "notas": "Área de experimentación y prototipado. Requiere inducción previa."
                }
            ]

            zonas_creadas = 0

            for zona_data in zonas_data:
                try:
                    # Buscar por nombre y ubicación (combinación única)
                    zona_obj, created = ZonaTrabajo.objects.get_or_create(
                        nombre=zona_data["nombre"],
                        ubicacion=zona_data["ubicacion"],
                        defaults={
                            "area": zona_data["area"],
                            "supervisor": zona_data["supervisor"],
                            "notas": zona_data["notas"],
                            "status": "ACTIVE"
                        }
                    )
                    
                    if created:
                        zonas_creadas += 1
                        self.stdout.write(f"Zona de trabajo creada: {zona_data['nombre']}")
                    else:
                        # Actualizar zona existente
                        zona_obj.area = zona_data["area"]
                        zona_obj.supervisor = zona_data["supervisor"]
                        zona_obj.notas = zona_data["notas"]
                        zona_obj.status = "ACTIVE"
                        zona_obj.save()
                        self.stdout.write(f"Zona de trabajo actualizada: {zona_data['nombre']}")

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error creando zona de trabajo {zona_data['nombre']}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"Se procesaron {len(zonas_data)} zonas de trabajo, {zonas_creadas} nuevas creadas"))