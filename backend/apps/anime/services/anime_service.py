from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta

from apps.anime.models import Anime
from apps.anime.models import AnimeStatus

from common.constants import PaginationConstants


class AnimeService:

    ALLOWED_ORDER_FIELDS = {
        "anime_name": "anime_name",
        "created_at": "created_at",
        "updated_at": "updated_at",
        "watched_episode": "watched_episode",
        "updated_till": "updated_till",
        "status": "status__status_name",
    }

    # ==========================
    # Anime Status
    # ==========================

    def create_status(self, user, validated_data):
        pass

    def update_status(self, user, status_id, validated_data):
        pass

    def list_status(self, user):
        pass

    def change_status_state(self, user, status_id):
        pass


    # ==========================
    # Anime
    # ==========================

    def create(self, user, validated_data):

        return Anime.objects.create(
            user=user,
            **validated_data
        )

    def update(self, user, anime_id, validated_data):

        anime = self._get(
            user,
            anime_id
        )

        if not anime:
            return None

        for field, value in validated_data.items():
            setattr(
                anime,
                field,
                value
            )

        anime.save()

        return anime

    def list(self, user, validated_data):

        queryset = self._get_queryset(
            user
        )

        queryset = self._search(
            queryset,
            validated_data
        )

        queryset = self._filter(
            queryset,
            validated_data
        )

        queryset = self._order(
            queryset,
            validated_data
        )

        return self._paginate(
            queryset,
            validated_data
        )

    def schedule_delete(self, user, anime_id):

        anime = self._get(
            user,
            anime_id
        )

        if not anime:
            return None

        anime.delete_status = True

        anime.deleted_at = (
            timezone.now() +
            timedelta(
                hours=user.security.anime_delete_after_hours
            )
        )

        anime.save(
            update_fields=[
                "delete_status",
                "deleted_at",
                "updated_at"
            ]
        )

        return anime

    def restore(self, user, anime_id):

        anime = self._get(
            user,
            anime_id
        )

        if not anime:
            return None

        anime.delete_status = False

        anime.deleted_at = None

        anime.save(
            update_fields=[
                "delete_status",
                "deleted_at",
                "updated_at"
            ]
        )

        return anime

    def permanent_delete(self, user, anime_id):

        anime = self._get(
            user,
            anime_id
        )

        if not anime:
            return False

        anime.delete()

        return True

    # ==========================
    # Private Helpers
    # ==========================

    def _get(self, user, anime_id):

        return Anime.objects.filter(
                user=user,
                anime_id=anime_id
                ).first()

    def _get_queryset(self, user):

        return Anime.objects.filter(user=user).select_related("status")

    def _search(self, queryset, validated_data):

        search = validated_data.get("search")

        if not search:
            return queryset

        return queryset.filter(
            Q(anime_name__icontains=search) |
            Q(notes__icontains=search) |
            Q(status__status_name__icontains=search)
        )

    def _filter(self, queryset, validated_data):

        status_id = validated_data.get("status_id")

        if status_id:

            queryset = queryset.filter(
                status_id=status_id
            )

        delete_status = validated_data.get("delete_status")

        if delete_status is not None:

            queryset = queryset.filter(
                delete_status=delete_status
            )

        return queryset

    def _order(self, queryset, validated_data):

        order_by = validated_data.get(
            "order_by",
            "created"
        )

        order_type = validated_data.get(
            "order_type",
            "desc"
        )

        order_by = self.ALLOWED_ORDER_FIELDS.get(
            order_by,
            "created_at"
        )

        if order_type == "desc":
            order_by = f"-{order_by}"

        return queryset.order_by(order_by)

    def _paginate(self, queryset, validated_data):

        paginator = Paginator(

            queryset,

            PaginationConstants.PAGE_SIZE

        )

        page = paginator.get_page(

            validated_data.get("page", 1)

        )

        return {
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page.number,
            "results": page.object_list,
        }

