# comics/management/commands/poblar_comics_externos.py
from django.core.management.base import BaseCommand
from comics.models import ComicExterno
from comics.services import get_embedding_document


COMICS_CURADOS = [
    {
        "nombre": "Saga",
        "autor": "Brian K. Vaughan",
        "descripcion": "Space opera sobre dos soldados de bandos opuestos que huyen con su hija recién nacida mientras son perseguidos por ambos lados de una guerra galáctica. Mezcla fantasía, ciencia ficción y drama familiar con arte visualmente impactante y personajes diversos."
    },
    {
        "nombre": "Akira",
        "autor": "Katsuhiro Otomo",
        "descripcion": "Manga cyberpunk ambientado en una Neo-Tokio post-apocalíptica. La historia sigue a Kaneda y Tetsuo, dos amigos de una banda de moteros, cuyo encuentro con un misterioso niño con poderes psíquicos desencadena el caos. Obra maestra del género con un arte detallado y una narrativa densa."
    },
    {
        "nombre": "Persepolis",
        "autor": "Marjane Satrapi",
        "descripcion": "Novela gráfica autobiográfica que narra la infancia y juventud de la autora en Irán durante y después de la Revolución Islámica. Con un estilo sencillo en blanco y negro, retrata la represión política, el exilio y la búsqueda de identidad."
    },
    {
        "nombre": "Maus",
        "autor": "Art Spiegelman",
        "descripcion": "Obra fundamental del cómic que narra la historia del padre del autor, un judío polaco superviviente del Holocausto, representando a los judíos como ratones y a los nazis como gatos. Entrevistas y memoria se entrelazan en una obra galardonada con el Premio Pulitzer."
    },
    {
        "nombre": "Watchmen",
        "autor": "Alan Moore",
        "descripcion": "Novela gráfica de superhéroes que deconstruye el género. Ambientada en una América alternativa de los años 80, sigue a un grupo de vigilantes retirados investigando el asesinato de uno de los suyos. Una obra compleja y madura sobre el poder, la moral y la condición humana."
    },
    {
        "nombre": "One Piece",
        "autor": "Eiichiro Oda",
        "descripcion": "Manga de aventuras que sigue a Monkey D. Luffy y su tripulación pirata en la búsqueda del tesoro legendario conocido como One Piece para convertirse en el Rey de los Piratas. Una de las series más exitosas y longevas del manga, con un vasto mundo y personajes entrañables."
    },
    {
        "nombre": "Berserk",
        "autor": "Kentaro Miura",
        "descripcion": "Manga de fantasía oscura que sigue a Guts, un guerrero solitario marcado por un destino trágico, en su lucha contra demonios y su búsqueda de venganza. Conocido por su arte detallado, su narrativa épica y sus temas maduros."
    },
    {
        "nombre": "Sandman",
        "autor": "Neil Gaiman",
        "descripcion": "Serie de cómics que sigue a Morfeo, el señor de los sueños, tras su liberación de décadas de cautiverio. Una obra que fusiona mitología, terror y fantasía, considerada una de las más ambiciosas y aclamadas del medio."
    },
    {
        "nombre": "Blacksad",
        "autor": "Juan Díaz Canales (guion) y Juanjo Guarnido (dibujo)",
        "descripcion": "Serie de cómics protagonizada por John Blacksad, un detective gato antropomórfico en una América de los años 50. Cada historia es un caso noir con crítica social, destacando por su espectacular arte pictórico."
    },
    {
        "nombre": "Tintin",
        "autor": "Hergé",
        "descripcion": "Serie clásica de cómics que sigue las aventuras de Tintín, un joven reportero, y su fiel perro Milú. Con un estilo de dibujo limpio conocido como 'línea clara', las historias abarcan misterio, aventura y exploración."
    },
    {
        "nombre": "Mafalda",
        "autor": "Quino",
        "descripcion": "Tira cómica argentina que sigue a Mafalda, una niña con una aguda conciencia social y política, y su grupo de amigos. Con humor inteligente y crítico, retrata la clase media argentina y las inquietudes de la época."
    },
    {
        "nombre": "Dragon Ball",
        "autor": "Akira Toriyama",
        "descripcion": "Manga de artes marciales y aventuras que sigue a Son Goku desde su infancia hasta la edad adulta, en su búsqueda de las siete esferas del dragón y su desarrollo como guerrero. Una obra que definió el shonen moderno."
    },
    {
        "nombre": "Death Note",
        "autor": "Tsugumi Ohba (guion) y Takeshi Obata (dibujo)",
        "descripcion": "Manga de suspenso psicológico que sigue a Light Yagami, un estudiante que encuentra un cuaderno que mata a quien sea cuyo nombre se escriba en él. Su duelo intelectual con el detective L es el eje de la historia."
    },
    {
        "nombre": "Fullmetal Alchemist",
        "autor": "Hiromu Arakawa",
        "descripcion": "Manga de aventuras y fantasía que sigue a los hermanos Edward y Alphonse Elric en su búsqueda de la Piedra Filosofal para recuperar sus cuerpos tras un fallido experimento de alquimia. Aclamado por su historia, personajes y construcción de mundo."
    },
    {
        "nombre": "Daredevil",
        "autor": "Varios (creado por Stan Lee y Bill Everett)",
        "descripcion": "Cómic de superhéroes que sigue a Matt Murdock, un abogado ciego de día y vigilante con sentidos sobrehumanos de noche, en el barrio de Hell's Kitchen. Conocido por sus historias noir y su tono más adulto y callejero."
    },
    {
        "nombre": "Batman",
        "autor": "Varios (creado por Bob Kane y Bill Finger)",
        "descripcion": "Cómic de superhéroes que sigue a Bruce Wayne, un multimillonario que de noche combate el crimen en Gotham City como Batman. Uno de los personajes más icónicos y versátiles de la cultura popular, con innumerables etapas y reinterpretaciones."
    },
    {
        "nombre": "Spiderman",
        "autor": "Varios (creado por Stan Lee y Steve Ditko)",
        "descripcion": "Cómic de superhéroes que sigue a Peter Parker, un adolescente que obtiene poderes arácnidos tras la picadura de una araña radiactiva. Sus historias equilibran acción, drama personal y responsabilidad."
    },
    {
        "nombre": "Hellboy",
        "autor": "Mike Mignola",
        "descripcion": "Cómic de terror y aventuras que sigue a Hellboy, un demonio invocado por los nazis pero criado por humanos, que trabaja para una agencia que combate lo sobrenatural. Destaca por su atmósfera gótica y el arte distintivo de Mignola."
    },
    {
        "nombre": "Cross Game",
        "autor": "Mitsuru Adachi",
        "descripcion": "Manga de béisbol y romance que sigue a Koh Kitamura, un joven talentoso que abandona el deporte tras una tragedia familiar, y su relación con las cuatro hermanas Tsukishima. Una historia cálida sobre el duelo, el crecimiento y la búsqueda de sueños."
    },
    {
        "nombre": "Y: el ultimo hombre",
        "autor": "Brian K. Vaughan (guion) y Pia Guerra (dibujo)",
        "descripcion": "Serie de cómics post-apocalíptica en la que una plaga mata a todos los mamíferos con cromosoma Y, excepto a Yorick Brown y su mono Ampersand. Yorick se convierte en el último hombre sobre la Tierra en un mundo gobernado por mujeres."
    },
]


class Command(BaseCommand):
    help = "Puebla la tabla ComicExterno con cómics conocidos y genera sus embeddings."

    def handle(self, *args, **options):
        exitosos = 0
        for i, data in enumerate(COMICS_CURADOS, 1):
            comic, created = ComicExterno.objects.get_or_create(
                nombre=data["nombre"],
                defaults={
                    "autor": data["autor"],
                    "descripcion": data["descripcion"],
                    "orden": i,
                },
            )

            if not comic.embedding:
                vector = get_embedding_document(data["descripcion"])
                if vector:
                    comic.embedding = vector
                    comic.save(update_fields=["embedding"])
                    exitosos += 1
                    self.stdout.write(f"[{i}] OK: {comic.nombre}")
                else:
                    self.stdout.write(f"[{i}] FALLO embedding: {comic.nombre}")
            else:
                self.stdout.write(f"[{i}] Ya existía: {comic.nombre}")

        self.stdout.write(self.style.SUCCESS(
            f"Listo. {exitosos} embeddings generados de {len(COMICS_CURADOS)} cómics."
        ))