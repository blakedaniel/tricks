# Generated by Django 4.2.3 on 2023-08-10 15:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0024_remove_round_players_round_game_alter_game_rounds"),
    ]

    operations = [
        migrations.AlterField(
            model_name="game",
            name="num_of_rounds",
            field=models.IntegerField(default=3),
        ),
        migrations.AlterField(
            model_name="game",
            name="players",
            field=models.ManyToManyField(blank=True, to="main.player"),
        ),
        migrations.AlterField(
            model_name="game",
            name="rounds",
            field=models.ManyToManyField(
                blank=True, related_name="cur_rounds", to="main.round"
            ),
        ),
        migrations.AlterField(
            model_name="player",
            name="hand",
            field=models.ManyToManyField(
                blank=True, related_name="hand", to="main.card"
            ),
        ),
        migrations.AlterField(
            model_name="round",
            name="deck",
            field=models.ManyToManyField(
                blank=True, related_name="deck", to="main.card"
            ),
        ),
        migrations.AlterField(
            model_name="round",
            name="game",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="main.game"
            ),
        ),
        migrations.AlterField(
            model_name="round",
            name="table",
            field=models.ManyToManyField(
                blank=True, related_name="table", to="main.card"
            ),
        ),
    ]
