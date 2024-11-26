from .models import Cast,Rating, Actor, Director,Movie
from django.db.models import Sum,Avg,Count,F,Q


def populate_database(actors_list, movies_list, directors_list, movie_rating_list):
    directors_map={}
    for director in directors_list:
        name=Director.objects.create(name=director['name'])
        directors_map[director['name']]=name


    actor_map = {}
    for actor in actors_list:
        obj, created = Actor.objects.create(actor_id=actor['actor_id'], name=actor['name'])
        actor_map[actor['actor_id']] = obj

    movies_map={}
    for movie in movies_list:
        director=directors_map[movie['director_id']]
        obj= Movie.objects.create(
            movie_id=movie['movie_id'],
            name=movie['name'],
            release_date=movie['release_date'],
            box_office_collection_in_crores=movie['box_office_collection_in_crores'],
            director=director,
        )
        movies_map[movie['movie_id']]=obj

        for cast in movie['cast']:
            actor = actor_map[cast['actor_id']]
            Cast.objects.get_or_create(
                movie=obj,
                actor=actor,
                role=cast['role'],
                is_debut_movie=cast.get('is_debut_movie', False)
            )

    for rating in movie_rating_list:
        movie = movies_map[rating['movie_id']]
        Rating.objects.get_or_create(
            movie=movie,
            rating_one_count=rating.get('rating_one_count', 0),
            rating_two_count=rating.get('rating_two_count', 0),
            rating_three_count=rating.get('rating_three_count', 0),
            rating_four_count=rating.get('rating_four_count', 0),
            rating_five_count=rating.get('rating_five_count', 0)
        )

    return "Database populated successfully!"



def get_no_of_distinct_movies_actor_acted(actor_id):
    no_of_movies = Cast.objects.filter(actor_id=actor_id).values('movie_id').distinct().count()
    return no_of_movies


def get_average_rating_of_movie(movie_obj):
    ratings = Rating.objects.filter(movie=movie_obj).aggregate(
        total_ratings=(
                F('rating_one_count') * 1 +
                F('rating_two_count') * 2 +
                F('rating_three_count') * 3 +
                F('rating_four_count') * 4 +
                F('rating_five_count') * 5
        ),
        total_counts=(
                F('rating_one_count') +
                F('rating_two_count') +
                F('rating_three_count') +
                F('rating_four_count') +
                F('rating_five_count')
        )
    )
    total_ratings = ratings['total_ratings']
    total_counts = ratings['total_counts']
    if total_counts == 0:
        return 0
    average_rating = total_ratings / total_counts
    return average_rating

def delete_movie_rating(movie_obj):
    Rating.objects.filter(movie=movie_obj).delete()


def get_all_actor_objects_acted_in_given_movies(movie_objs):
    movies = Cast.objects.filter(movie__in=movie_objs).select_related('actor', 'movie')
    result={}
    for each_movie in movie_objs:
        if each_movie in movies:
            result['Actor:']=each_movie['actor__actor_id']
    return result

def update_director_for_given_movie(movie_obj, director_obj):
    movie=Movie.objects.filter(movie=movie_obj)
    if movie:
        movie.director=director_obj

def get_distinct_movies_acted_by_actor_whose_name_contains_john():
    movies_acted_by_jhon=Cast.objects.filter(actor__name__icontains='jhon').select_related(['movie','actor']).distinct()
    return movies_acted_by_jhon

def remove_all_actors_from_given_movie(movie_obj):
    movie=Cast.objects.filter(movie=movie_obj).select_related(['movie','actor']).delete()


def get_all_rating_objects_for_given_movies(movie_objs):
    ratings_queryset = Rating.objects.filter(movie__in=movie_objs).select_related('movie')
    ratings = {}
    for rating in ratings_queryset:
        if rating.movie.id not in ratings:
            ratings[rating.movie.id] = []
        ratings[rating.movie.id].append(rating)

    return ratings

def get_movies_by_given_movie_names(movie_names):
    movies = Movie.objects.filter(name__in=movie_names)
    return movies

def get_movies_released_in_summer_in_given_years():
    get_movies = Movie.objects.filter(
        release_date__month__in=[5, 6, 7],
        release_date__year__range=(2005, 2010)
    )
    return get_movies

def get_movie_names_with_actor_name_ending_with_smith():
     get_movies = Cast.objects.filter(actor__name__iendswith='smith').select_related('movie', 'actor')
     result = {}
     for each_movie in get_movies:
         result[each_movie.movie.name] = each_movie.actor.name

     return result

def get_movie_names_with_ratings_in_given_range():
    get_movies = Rating.objects.filter(rating_three_count__range=(1000, 3000)).select_related('movie')
    movie_names = [rating.movie.name for rating in get_movies]

    return movie_names

def get_movie_directors_in_given_year():
    get_directors = Movie.objects.filter(release_date__year=2000).select_related('director')
    directors = {movie.name: movie.director.name for movie in get_directors}

    return directors

def get_actor_names_debuted_in_21st_century():
    get_actors = Cast.objects.filter(is_debut_movie=True, movie__release_date__year__gte=2000).select_related('actor', 'movie').distinct()
    actor_names = [cast.actor.name for cast in get_actors]

    return actor_names

def get_director_names_containing_big_as_well_as_movie_in_may():
    get_directors = Cast.objects.filter(
        Q(actor__name__iendswith='big') & Q(movie__release_date__month=5)
    ).select_related('movie__director').distinct()
    director_names = {cast.movie.director.name for cast in get_directors}
    return director_names

def get_director_names_containing_big_and_movie():
    get_directors = Cast.objects.filter(
        actor__name__icontains="big",
        movie__release_date__month=5
    ).select_related('movie__director')
    director_names = {cast.movie.director.name for cast in get_directors if cast.movie.director}
    return director_names

def reset_ratings_for_movies_in_this_year():
    movies = Rating.objects.filter(movie__release_date__year=2000)
    for each_movie in movies:
        each_movie.rating_one_count=0
        each_movie.rating_two_count=0
        each_movie.rating_three_count=0
        each_movie.rating_four_count=0
        each_movie.rating_five_count=0

        each_movie.save()

def get_average_box_office_collections():
    collection = Movie.objects.aggregate(Avg('box_office_collection_in_crores'))['box_office_collection_in_crores__avg']
    return collection

def get_movies_with_distinct_actors_count():
    movies_with_actor_count = Movie.objects.annotate(distinct_actors_count=Count('cast__actor', distinct=True))
    return movies_with_actor_count

def get_roles_count_for_each_movie():
    roles_count = Cast.objects.values('movie').annotate(count=Count('role', distinct=True))
    return roles_count

def get_role_frequency():
    freq = Cast.objects.values('role').annotate(movie_count=Count('movie', distinct=True))
    return freq

def get_role_frequency_in_order():
    freq = Cast.objects.values('role').annotate(movie_count=Count('movie', distinct=True)).order_by('movie_count')
    return freq


def get_no_of_movies_and_distinct_roles_for_each_actor():
    result = Cast.objects.values('actor').annotate(movie_count=Count('movie', distinct=True),role_count=Count('role', distinct=True))
    return result

def get_movies_with_atleast_forty_actors():
    get_movies = Cast.objects.values('movie').annotate(actor_count=Count('actor', distinct=True)).filter(actor_count__gte=40)
    return get_movies

def get_average_no_of_actors_for_all_movies():
    avg_no_of_actors = Cast.objects.values('movie').annotate(actor_count=Count('actor')).aggregate(Avg('actor_count'))['actor_count__avg']
    return avg_no_of_actors


def remove_all_actors_from_given_movie(movie_object):
    movie_object.actors.clear()
    movie_object.save()

def get_all_rating_objects_for_given_movies(movie_objs):
    rating_objects=[]
    ratings = Rating.objects.filter(movie__in=movie_objs)
    for each_item in ratings:
        rating_objects.append((
            each_item.rating_one_count,
            each_item.rating_two_count,
            each_item.rating_three_count,
            each_item.rating_four_count,
            each_item.rating_five_count
        ))

    return rating_objects

def get_movies_by_given_movie_names(movie_names):
    movies = Movie.objects.filter(name__in=movie_names)
    return movies

def get_all_actor_objects_acted_in_given_movies(movie_objs):
    actor_objects = Cast.objects.filter(movie__in=movie_objs).select_related('actor').distinct()
    return actor_objects

def get_actor_movies_released_in_year_greater_than_or_equal_to_2000():
    result=list(Cast.objects.filter(movie__released_date__year__gte=2000).select_related('movie').distinct())
    return result
def reset_ratings_for_movies_in_given_year(year):
    movies = Rating.objects.filter(movie__release_date__year=year).select_related('movie')
    for each_movie in movies:
        each_movie.rating_one_count=0
        each_movie.rating_two_count=0
        each_movie.rating_three_count=0
        each_movie.rating_four_count=0
        each_movie.rating_five_count=0
        each_movie.save()