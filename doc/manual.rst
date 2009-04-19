====================================================
Edustajistovaalien äänioikeuden tarkastusjärjestelmä
====================================================

:Date: 2009-04-19
:Author: Jyrki Pulliainen
:Organization: Turun yliopiston ylioppilaskunta
:Copyright: Copyright 2009 Jyrki Pulliainen.
:License: Creative Commons Nimeä-Tarttuva 1.0 Suomi

Äänioikeuden tarkastusjärjestelmän funktio on estää päällekäistä
äänestystä edustajistovaaleissa. Järjestelmä tarjoaa reaaliaikaista
tietoa jo äänestäneistä ihmisistä.

Dokumentissa esitetyt URL:t ovat kaikki suhteellisia vaalipalvelimen
osoitteeseen, jollei toisin mainita.

---------------------
Laitteistovaatimukset
---------------------

Tarkastusjärjestelmä on asiakas-palvelinpohjainen web-sovellus.
Järjestelmän toiminta selainpäässä perustuu pitkälti Javascriptiin ja
asynkronisiin kutsuihin palvelimelle.

Asiakaspää
==========


* Tietokone verkkoyhteydellä, esim. wlan SparkNetin yli

* Moderni selain (testatut selaimet Firefox 3.0 sekä IE 7)

Palvelinpuoli
=============


* Pythonia tukeva www-palvelinohjelmisto. Vaihtoehdot:

  * Apache 2 + mod_python

    * Helpoin pistää pystyyn

    * Testattu käytännössä

  * Apache 2 + mod_wsgi

    * Ei takeita toimivuudesta

  * Lighttpd + FastCGI

    * Enemmän käsityötä

  * Vuosina 2007 sekä 2009 käytetty sähköinen äänestysjärjestelmä
    nojaa jo valmiiksi Apachen käyttöön, joten Apache on tämän takia
    parempi ratkaisu

* Python 2.4+

* Django_ 1.0

* PostgreSQL 8.x (myös muut tietokantamoottorit mahdollisia)

* Simplejson_

.. _Django: http://www.djangoproject.com

.. _Simplejson: http://www.undefined.org/python/

Kehitysympäristö
================

Kehitysympäristön vaatimukset ovat lähes identtiset palvelin- sekä
asiakasympäristön kanssa. Yksikkötestien ajamiseen tarvitaan Nose_.

.. _Nose: http://somethingaboutorange.com/mrl/projects/nose/

-------
Asennus
-------

Seuraava asennusohje koskee järjestelmän asentamista Apache2 +
mod_python -ympäristöön. Tämä olettaa, että www-palvelin vastaa
osoitteessa ``vaalit.tyy.fi``.

1. Kopioi tarkastusjärjestelmän tiedostot hakemistoon (esim.
   ``/srv/tyy-vaali/``)

2. Luo Apacheen uusi entry ``vaalit.tyy.fi`` VirtualHostin alle::

    <Location /tarkistus>
        AuthType shibboleth
        ShibRequireSession On
        ShibUseHeaders On
        require valid-user
        SetHandler mod_python
        PythonHandler django.core.handlers.modpython
        PythonPath "['/srv/tyy-vaali/'] + sys.path"
        SetEnv DJANGO_SETTINGS_MODULE aanikone.settings_prod
        PythonDebug Off
    </Location>

3. Luo tiedosto ``/srv/tyy-vaali/aanikone/settings_prod.py``::

    # -*- coding: utf-8 -*-
    from aanikone.settings import *

    #DEBUG = False
    DEBUG = True

    DATABASE_HOST = '127.0.0.1'
    DATABASE_ENGINE = 'postgresql'
    DATABASE_NAME = 'webvoter'
    DATABASE_USER = 'webvoter'

    try:
        f = open('/srv/tyy-vaali/aanikone/credentials', 'r')
    except:
        raise
    else:
        DATABASE_PASSWORD = f.read()
        f.close()
        del f


    MEDIA_ROOT = '/var/www/media/'

    SECRET_KEY = '<syötä-tähän-jotain-puppaa>'

    TEMPLATE_DIRS = (
        '/srv/tyy-vaali/templates/',
    )

  ``/srv/tyy-vaali/aanikone/credentials``-tiedoston sisältö on
  tuotantokannan salasana (ilman rivinvaihtoja).

4. Luo tuotantokannan taulut::

    cd /srv/tyy-vaali/aanikone/
    python manage.py syncdb

   *Huom!* Kysyttäessä pääkäyttäjän käyttäjätunnusta, syötä oma
   yliopiston käyttäjätunnuksesi.

5. Käynnistä Apache uudelleen::

    /etc/init.d/apache2 force-reload

6. Kokeile, että asennus toimii vierailemalla osoitteessa
   ``http://vaalit.tyy.fi/tarkistus/``

7. Lisää loput käyttäjät sekä äänestyspisteet ylläpitoliittymän kautta
   osoitteesta ``/tarkistus/admin/``

--------
Toiminta
--------

Käyttäjäautentikaatio
=====================

Käyttäjäautentikaatio hoidetaan Shibbolethin avulla.
Shibboleth-autentikaation voi tarvittaessa kytkeä pois päältä
poistamalla rivin::

  AUTHENTICATION_BACKENDS = ('aanikone.auth.ShibbolethBackend',)

settings.py-tiedostosta.

Shibboleth-autentikaatiossa verrataan Shibbolethin antamaa
käyttäjätunnusta tunnettuihin käyttäjiin. Käyttäjät voi lisätä joko
admin-liittymän kautta osoitteessa ``/tarkistus/admin/``
(Shibboleth-autentikaation tulee tällöin olla pois päältä) tai
komentoriviltä komennolla ``python manage.py shell`` (``aanikone``
hakemistossa, joka avaa käyttäjälle Python-komentorivin, jonka kautta
käyttäjiä voi lisätä::

  >>> from django.contrib.auth.models import User
  >>> User(username="foo").save()

Asennus_ kysyy myös pääkäyttäjän käyttäjätunnusta sekä salasanaa.
Asettamalla tämän Shibboleth-tunnukseksesi, ei Shibboleth
autentikaatiota tarvitse kytkeä pois päältä päästäksesi
admin-liittymään.

Shibboleth-tunnus
-----------------

Shibboleth-tunnus päätellään Shibbolethin lisäämistä headereista.
Turun yliopiston tapauksessa tämä on ``HTTP_MAIL`` header. Header on
muodossa ``käyttäjätunnus@utu.fi``.

Autentikoinnin koodi löytyy tiedostosta ``aanikone/auth.py``.

Vuoden 2009 erikoistapaus
~~~~~~~~~~~~~~~~~~~~~~~~~

Vuonna 2009 vaaleissa oli kahden eri organisaation tunnukset, Turun
kauppakorkeakoulun sekä Turun yliopiston. Kauppakorkeakoulun
Shibboleth tarjosi käyttäjätunnuksen ``HTTP_UID`` headerissa
sellaisenaan.

Äänestyspisteet
===============

Äänestyspisteitä voi lisätä hallintaliittymän kautta osoitteessa ``/tarkistus/admin/``


Äänestäjän tarkastaminen
========================

Toiminta äänestyspisteellä
--------------------------

Mitä ikinä äänestyspisteellä tekeekin, tulee järjestelmän kehotuksia
noudattaa. *Äänestyslipuketta ei tule antaa tai leimata, mikäli
järjestelmä ei niin sano*.

Äänioikeuden tarkastaminen tapahtuu seuraavasti:

* Kirjaudu sisään järjestelmään oppilaitoksen tunnuksilla osoitteessa
  ``/tarkistus/``

* Valitse pudotusvalikosta oikea äänestyspiste

* Syötä opiskelijanumero sille varattuun kenttään ja paina
  OK-painiketta.

  * *Huom!* Tässä oli poikkeuksena vuoden 2009 edustajistovaalit,
     joissa oli kahden organisaation äänestys ja täten kaksi
     "ok-painiketta". Tämän takia vuoden 2011 äänestystä varten
     ohjelman toimintaa pitänee muuttaa hieman.

* Noudata järjestelmän antamia ohjeita

**Tämä rutiini tulee käydä läpi *aina* kun äänestäjä saapuu
äänestyspisteelle, huolimatta siitä, onko äänestäjä uusi vai
palauttaako hän äänestyslipukkeen.**

Järjestelmän toiminta
---------------------

Kun äänestäjä saapuu äänestyspisteelle ja äänestäjän opiskelijanumero
syötetään järjestelmään, tapahtuu seuraavaa:

1. Järjestelmä suorittaa asynkronisen kyselyn palvelimelle
varmistaakseen äänestäjän henkilöllisyyden

2. Henkilöllisyys varmistetaan vaalivirkailijalta
OK/Cancel-dialogilla ("Esimerkki, Erkki Petteri, Turun yliopisto. Onko
oikein?")

  * Mikäli käyttäjä ei paina OK, tapahtuma keskeytetään ja käyttäjä
    voi syöttää opiskelijanumeron uudelleen.

3. Henkilöllisyyden varmistamisen jälkeen suoritetaan asynkroninen
kysely palvelimelle, joka tarkistaa onko henkilö jo äänestänyt.

    * Mikäli henkilö ei ole äänestänyt, merkataan hänet äänestäneeksi
      ja pyydetään virkailijaa antamaan äänestyslipuke

    * Mikäli henkilö on äänestänyt, tarkastetaan onko hän palaava
      lippuäänestäjä. Mikäli on, käsketään ottamaan lippu vastaan.
      Mikäli ei, ilmoitetaan, että henkilö on jo äänestänyt muualla,
      eikä lippua tule antaa.

Äänestäjä merkataan siis äänestäneeksi jo lippua annettaessa. Tämä
estää mahdollisuuden, jossa äänestäjä voisi hakea lipun ja äänestää
silti sähköisesti.


Tulevaisuudensuunnitelmia
=========================

Järjestelmässä on vielä riittävästi kehitettävää tulevaisuutta varten:

* Python-paketointi (setup.py & co), helpottaisi seuraavaa kohtaa

* Debian-paketointi, helpottaisi asennusta

* Yleistä silottelua, testien lisäämistä

* Vuonna 2009 ulkona olevien äänestyslippujen listassa oli jokin vika,
  jonka takia se ei näkynyt kaikilla koneilla. Tätä sietäisi tutkia.

Koodin sekä tämän dokkarin sijainti
===================================

GPL-lisensoitu koodi sekä tämän dokkarin viimeisin versio majailevat
molemmat GitHubissa osoitteessa

  http://github.com/nailor/tyy-vaali

