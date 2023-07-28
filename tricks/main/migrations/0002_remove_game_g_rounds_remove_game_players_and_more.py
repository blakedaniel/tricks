# Generated by Django 4.2.3 on 2023-07-21 22:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="game",
            name="g_rounds",
        ),
        migrations.RemoveField(
            model_name="game",
            name="players",
        ),
        migrations.RemoveField(
            model_name="player",
            name="hand",
        ),
        migrations.RemoveField(
            model_name="player",
            name="wins",
        ),
        migrations.RemoveField(
            model_name="round",
            name="players",
        ),
        migrations.RemoveField(
            model_name="trick",
            name="active_player",
        ),
        migrations.AddField(
            model_name="card",
            name="game",
            field=models.ForeignKey(
                blank=True,
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="main.game",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="card",
            name="player",
            field=models.ForeignKey(
                blank=True,
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="main.player",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="card",
            name="status",
            field=models.TextField(
                blank=True,
                choices=[("d", "Deck"), ("h", "Hand"), ("p", "Played"), ("t", "Trump")],
                default="d",
            ),
        ),
        migrations.AddField(
            model_name="game",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="player",
            name="active",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="player",
            name="game",
            field=models.ForeignKey(
                default=1, on_delete=django.db.models.deletion.CASCADE, to="main.game"
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="player",
            name="playe_pos",
            field=models.IntegerField(blank=True, default=1, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="round",
            name="game",
            field=models.ForeignKey(
                default=1, on_delete=django.db.models.deletion.CASCADE, to="main.game"
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="trick",
            name="trick_rnd",
            field=models.PositiveSmallIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name="card",
            name="rank",
            field=models.CharField(
                choices=[
                    ("2", "2"),
                    ("3", "3"),
                    ("4", "4"),
                    ("5", "5"),
                    ("6", "6"),
                    ("7", "7"),
                    ("8", "8"),
                    ("9", "9"),
                    ("10", "10"),
                    ("j", "Jack"),
                    ("q", "Queen"),
                    ("k", "King"),
                    ("a", "Ace"),
                ],
                max_length=5,
            ),
        ),
        migrations.AlterField(
            model_name="card",
            name="suit",
            field=models.CharField(
                choices=[
                    ("h", "Hearts"),
                    ("d", "Diamonds"),
                    ("c", "Clubs"),
                    ("s", "Spades"),
                ],
                max_length=10,
            ),
        ),
        migrations.AlterField(
            model_name="round",
            name="cur_round",
            field=models.IntegerField(default=6),
        ),
        migrations.AlterField(
            model_name="trick",
            name="round",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="main.round"
            ),
        ),
    ]
