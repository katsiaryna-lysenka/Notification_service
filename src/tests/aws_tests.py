from unittest.mock import Mock, patch

import pytest

from src.aws_file import send_email


@pytest.mark.asyncio
async def test_send_email():
    subject = "Instructions for changing your password"
    body = (
        "Reset your password by clicking the following link: "
        "http://127.0.0.1:5000/auth/set-new-password?token="
        "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoicmVzZX"
        "QiLCJzdWIiOiJ3d3dAZ21haWwuY29tIiwicmVzZXRfdG9rZW4iOnRydW"
        "UsImV4cCI6MTcxNDkzNTc5MSwiaWF0IjoxNzE0NzYyOTkxfQ.aeHdb51"
        "hOqyaOaLOPQiK_G2amkI6XDVXsyLRfmt8_GaWHorJ5AjOt8ildNu12Sk"
        "L_aLkPAvCf0JHfIE1qRr6DwjhA_gFpHM7mVt5wmICRGru8uJAphqYHj7i"
        "e3EjNG8sw3UiJmXqkNDz2yhsv2qisxDStXmiRw6dfs2WoYlLHGhvZEXMp"
        "BIeSBY_UELINy0sxrbkPoT3oJPeG7U87xhbFIu_w7GTkE0nRdVr3P-NLS"
        "WM0mIPaxeJ1ueiX4q_37rcQm-Y6IvSthqWRvH9Q07m_U6IDAubFj8KQiK"
        "QpDEbWGKI4M-XxwbYTJsuBz6AsQ1i1n_v8RRDtm8J8mESXy-viA\n"
        "The link will deactivate in 5 minutes"
    )
    recipient = "katy@gmail.com"

    mock_s3_client = Mock()
    mock_ses_client = Mock()

    with patch("src.aws_file.boto3.client") as mock_boto3_client:
        mock_boto3_client.side_effect = [mock_s3_client, mock_ses_client]

        result = await send_email(subject, body, recipient)

        mock_s3_client.create_bucket.assert_called_once_with(Bucket="my-test-bucket")

        mock_ses_client.verify_email_identity.assert_called_once_with(
            EmailAddress="katsiaryna.lysenka@innowise.com"
        )

        mock_ses_client.send_email.assert_called_once_with(
            Source="katsiaryna.lysenka@innowise.com",
            Destination={"ToAddresses": [recipient]},
            Message={"Subject": {"Data": subject}, "Body": {"Text": {"Data": body}}},
        )

        assert result is True
