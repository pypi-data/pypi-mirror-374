import textwrap
import uuid

from pathlib import Path

import pytest

from dbrownell_Email.SmtpMailer import SmtpMailer


# ----------------------------------------------------------------------
def test_ToString():
    mailer = SmtpMailer("host", "username", "password", "from_name", "from_email", ssl=True, port=123)

    assert mailer.ToString() == textwrap.dedent(
        """\
        host        : host
        username    : username
        password    : ****
        from_name   : from_name
        from_email  : from_email
        ssl         : True
        port        : 123
        """,
    )


# ----------------------------------------------------------------------
def test_SaveAndLoad():
    profile_name = str(uuid.uuid4())
    profile_filename = Path("~").expanduser() / f"{profile_name}{SmtpMailer.PROFILE_EXTENSION}"

    mailer = _CreateSmtpMailer()

    # Save the profile
    assert not profile_filename.exists(), profile_filename
    mailer.Save(profile_name)
    assert profile_filename.exists(), profile_filename

    # Load the profile
    loaded_mailer = SmtpMailer.Load(profile_name)
    assert loaded_mailer == mailer

    # Remove the profile file
    profile_filename.unlink()


# ----------------------------------------------------------------------
def test_LoadError():
    with pytest.raises(Exception, match="'Does not exist' is not a recognized profile name."):
        SmtpMailer.Load("Does not exist")


# ----------------------------------------------------------------------
def test_EnumProfiles():
    # Create a couple of profiles
    mailer1 = _CreateSmtpMailer()
    mailer2 = _CreateSmtpMailer()

    mailer1.Save(mailer1.host)
    mailer2.Save(mailer2.host)

    # Find the profiles
    found_mailer1 = False
    found_mailer2 = False

    for profile in SmtpMailer.EnumProfiles():
        if profile == mailer1.host:
            assert found_mailer1 is False
            found_mailer1 = True
        elif profile == mailer2.host:
            assert found_mailer2 is False
            found_mailer2 = True

    assert found_mailer1 is True
    assert found_mailer2 is True

    (Path("~").expanduser() / f"{mailer1.host}{SmtpMailer.PROFILE_EXTENSION}").unlink()
    (Path("~").expanduser() / f"{mailer2.host}{SmtpMailer.PROFILE_EXTENSION}").unlink()


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _CreateSmtpMailer(
    host: str | None = None,
    username: str | None = None,
    password: str | None = None,
    from_name: str | None = None,
    from_email: str | None = None,
    ssl: bool | None = None,
    port: int | None = None,
) -> SmtpMailer:
    return SmtpMailer(
        host or str(uuid.uuid4()),
        username or str(uuid.uuid4()),
        password or str(uuid.uuid4()),
        from_name or str(uuid.uuid4()),
        from_email or str(uuid.uuid4()),
        ssl=ssl if ssl is not None else True,
        port=port,
    )
