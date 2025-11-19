from __future__ import annotations

from django.db import models
from tree_queries.models import TreeNode


class Category(TreeNode):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    description = models.TextField(blank=True)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="children")
    is_active = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)
    icon = models.CharField(max_length=128, blank=True)
    meta = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta(TreeNode.Meta):
        ordering = ("parent__id", "position", "name")
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self) -> str:  # pragma: no cover
        return self.name


