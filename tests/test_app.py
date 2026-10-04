import pytest
from pathlib import Path

# Test "de fumée" : l'app tourne de bout en bout sans exception.
# Ignoré si streamlit n'est pas installé dans le venv.
streamlit_testing = pytest.importorskip("streamlit.testing.v1")

# Chemin de app.py à la racine du projet (AppTest résout les chemins depuis tests/)
CHEMIN_APP = str(Path(__file__).parent.parent / "app.py")


def test_app_se_lance_sans_erreur():
    app = streamlit_testing.AppTest.from_file(CHEMIN_APP, default_timeout=120)
    app.run()

    assert not app.exception
    # Aucun avertissement affiché (ex. option dépréciée de st.pyplot)
    assert not app.warning
    assert len(app.tabs) == 4
    # Les 4 graphiques sont en Altair (dessinés par le navigateur) et aucun n'est une image
    # matplotlib, qui se déformait parfois quand on changeait les paramètres
    assert len(app.get("vega_lite_chart")) == 4
    assert len(app.get("image")) == 0


def test_app_put_et_gros_choc():
    app = streamlit_testing.AppTest.from_file(CHEMIN_APP, default_timeout=120)
    app.run()

    app.sidebar.radio[0].set_value("put")
    app.slider[0].set_value(-20.0)   # choc de spot -20%
    app.run()

    assert not app.exception


def test_app_maturite_depassee_affiche_une_erreur():
    # 60 jours écoulés sur une option de maturité 0.1 an : le module refuse,
    # l'app doit afficher le message au lieu de planter
    app = streamlit_testing.AppTest.from_file(CHEMIN_APP, default_timeout=120)
    app.run()

    app.sidebar.number_input[2].set_value(0.1)
    app.slider[3].set_value(60)
    app.run()

    assert not app.exception
    assert any("maturité" in erreur.value for erreur in app.error)
