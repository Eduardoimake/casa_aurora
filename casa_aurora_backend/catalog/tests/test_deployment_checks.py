"""Testes das verificações de implantação da Casa Aurora."""

from django.core.checks import Tags, run_checks
from django.test import SimpleTestCase, override_settings

from catalog.deployment_checks import check_casa_aurora_deployment


class DeploymentCheckTests(SimpleTestCase):
    def issue_ids(self):
        return {
            issue.id
            for issue in check_casa_aurora_deployment(
                app_configs=None
            )
        }

    @override_settings(
        DEBUG=False,
        SECRET_KEY="chave-de-teste-diferente-da-chave-local",
        SESSION_COOKIE_SECURE=True,
        CSRF_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        CORS_ALLOW_CREDENTIALS=True,
        CORS_ALLOW_ALL_ORIGINS=False,
        SECURE_PROXY_SSL_HEADER=None,
    )
    def test_configuracao_basica_segura_nao_emite_avisos_do_catalogo(self):
        self.assertEqual(self.issue_ids(), set())

    @override_settings(
        DEBUG=True,
        SECRET_KEY="django-insecure-local-only-change-before-deployment",
        SESSION_COOKIE_SECURE=False,
        CSRF_COOKIE_SECURE=False,
        SESSION_COOKIE_HTTPONLY=False,
        CORS_ALLOW_CREDENTIALS=False,
        CORS_ALLOW_ALL_ORIGINS=True,
        MIDDLEWARE=[],
        SECURE_PROXY_SSL_HEADER=(
            "HTTP_X_FORWARDED_PROTO",
            "https",
        ),
    )
    def test_configuracoes_inseguras_sao_reportadas(self):
        self.assertEqual(
            self.issue_ids(),
            {
                "catalog.W001",
                "catalog.W002",
                "catalog.W003",
                "catalog.W004",
                "catalog.W005",
                "catalog.W006",
                "catalog.W007",
                "catalog.W008",
                "catalog.W009",
            },
        )

    def test_checks_especificos_nao_aparecem_na_rotina_comum(self):
        ids = {
            issue.id
            for issue in run_checks(
                tags=[Tags.security],
                include_deployment_checks=False,
            )
        }

        self.assertFalse(
            any(issue_id.startswith("catalog.W") for issue_id in ids)
        )

    def test_checks_especificos_aparecem_em_deploy(self):
        with override_settings(
            DEBUG=True,
            SECRET_KEY="django-insecure-local-only-change-before-deployment",
        ):
            ids = {
                issue.id
                for issue in run_checks(
                    include_deployment_checks=True,
                )
            }

        self.assertIn("catalog.W001", ids)
        self.assertIn("catalog.W002", ids)