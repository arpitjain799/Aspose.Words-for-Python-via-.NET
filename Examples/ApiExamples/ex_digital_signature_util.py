# Copyright (c) 2001-2023 Aspose Pty Ltd. All Rights Reserved.
#
# This file is part of Aspose.Words. The source code in this file
# is only intended as a supplement to the documentation, and is provided
# "as is", without warranty of any kind, either expressed or implied.

from datetime import datetime

import aspose.words as aw

from api_example_base import ApiExampleBase, MY_DIR, ARTIFACTS_DIR

class ExDigitalSignatureUtil(ApiExampleBase):

    def test_load(self):

        #ExStart
        #ExFor:DigitalSignatureUtil
        #ExFor:DigitalSignatureUtil.load_signatures(str)
        #ExFor:DigitalSignatureUtil.load_signatures(BytesIO)
        #ExSummary:Shows how to load signatures from a digitally signed document.
        # There are two ways of loading a signed document's collection of digital signatures using the DigitalSignatureUtil class.
        # 1 -  Load from a document from a local file system filename:
        digital_signatures = aw.digitalsignatures.DigitalSignatureUtil.load_signatures(MY_DIR + "Digitally signed.docx")

        # If this collection is nonempty, then we can verify that the document is digitally signed.
        self.assertEqual(1, digital_signatures.count)

        # 2 -  Load from a document from a FileStream:
        with open(MY_DIR + "Digitally signed.docx", "rb") as stream:
            digital_signatures = aw.digitalsignatures.DigitalSignatureUtil.load_signatures(stream)
            self.assertEqual(1, digital_signatures.count)

        #ExEnd

    def test_remove(self):

        #ExStart
        #ExFor:DigitalSignatureUtil
        #ExFor:DigitalSignatureUtil.load_signatures(str)
        #ExFor:DigitalSignatureUtil.remove_all_signatures(BytesIO,BytesIO)
        #ExFor:DigitalSignatureUtil.remove_all_signatures(str,str)
        #ExSummary:Shows how to remove digital signatures from a digitally signed document.
        # There are two ways of using the DigitalSignatureUtil class to remove digital signatures
        # from a signed document by saving an unsigned copy of it somewhere else in the local file system.
        # 1 - Determine the locations of both the signed document and the unsigned copy by filename strings:
        aw.digitalsignatures.DigitalSignatureUtil.remove_all_signatures(
            MY_DIR + "Digitally signed.docx",
            ARTIFACTS_DIR + "DigitalSignatureUtil.load_and_remove.from_string.docx")

        # 2 - Determine the locations of both the signed document and the unsigned copy by file streams:
        with open(MY_DIR + "Digitally signed.docx", "rb") as stream_in:
            with open(ARTIFACTS_DIR + "DigitalSignatureUtil.load_and_remove.from_stream.docx", "wb") as stream_out:
                aw.digitalsignatures.DigitalSignatureUtil.remove_all_signatures(stream_in, stream_out)

        # Verify that both our output documents have no digital signatures.
        self.assertListEqual([], aw.digitalsignatures.DigitalSignatureUtil.load_signatures(ARTIFACTS_DIR + "DigitalSignatureUtil.load_and_remove.from_string.docx"))
        self.assertListEqual([], aw.digitalsignatures.DigitalSignatureUtil.load_signatures(ARTIFACTS_DIR + "DigitalSignatureUtil.load_and_remove.from_stream.docx"))
        #ExEnd

    # WORDSNET-16868
    def test_sign_document(self):

        #ExStart
        #ExFor:CertificateHolder
        #ExFor:CertificateHolder.create(str,str)
        #ExFor:DigitalSignatureUtil.sign(BytesIO,BytesIO,CertificateHolder,SignOptions)
        #ExFor:SignOptions.comments
        #ExFor:SignOptions.sign_time
        #ExSummary:Shows how to digitally sign documents.
        # Create an X.509 certificate from a PKCS#12 store, which should contain a private key.
        certificate_holder = aw.digitalsignatures.CertificateHolder.create(MY_DIR + "morzal.pfx", "aw")

        # Create a comment and date which will be applied with our new digital signature.
        sign_options = aw.digitalsignatures.SignOptions()
        sign_options.comments = "My comment"
        sign_options.sign_time = datetime.now()

        # Take an unsigned document from the local file system via a file stream,
        # then create a signed copy of it determined by the filename of the output file stream.
        with open(MY_DIR + "Document.docx", "rb") as stream_in:
            with open(ARTIFACTS_DIR + "DigitalSignatureUtil.sign_document.docx", "wb") as stream_out:
                aw.digitalsignatures.DigitalSignatureUtil.sign(stream_in, stream_out, certificate_holder, sign_options)

        #ExEnd

        with open(ARTIFACTS_DIR + "DigitalSignatureUtil.sign_document.docx", "rb") as stream:
            digital_signatures = aw.digitalsignatures.DigitalSignatureUtil.load_signatures(stream)
            self.assertEqual(1, digital_signatures.count)

            signature = digital_signatures[0]

            self.assertTrue(signature.is_valid)
            self.assertEqual(aw.digitalsignatures.DigitalSignatureType.XML_DSIG, signature.signature_type)
            self.assertEqual(sign_options.sign_time, signature.sign_time)
            self.assertEqual("My comment", signature.comments)

    # WORDSNET-16868
    def test_decryption_password(self):

        #ExStart
        #ExFor:CertificateHolder
        #ExFor:SignOptions.decryption_password
        #ExFor:LoadOptions.password
        #ExSummary:Shows how to sign encrypted document file.
        # Create an X.509 certificate from a PKCS#12 store, which should contain a private key.
        certificate_holder = aw.digitalsignatures.CertificateHolder.create(MY_DIR + "morzal.pfx", "aw")

        # Create a comment, date, and decryption password which will be applied with our new digital signature.
        sign_options = aw.digitalsignatures.SignOptions()
        sign_options.comments = "Comment"
        sign_options.sign_time = datetime.now()
        sign_options.decryption_password = "docPassword"

        # Set a local system filename for the unsigned input document, and an output filename for its new digitally signed copy.
        input_file_name = MY_DIR + "Encrypted.docx"
        output_file_name = ARTIFACTS_DIR + "DigitalSignatureUtil.decryption_password.docx"

        aw.digitalsignatures.DigitalSignatureUtil.sign(input_file_name, output_file_name, certificate_holder, sign_options)
        #ExEnd

        # Open encrypted document from a file.
        load_options = aw.loading.LoadOptions("docPassword")
        self.assertEqual(sign_options.decryption_password, load_options.password)

        # Check that encrypted document was successfully signed.
        signed_doc = aw.Document(output_file_name, load_options)
        signatures = signed_doc.digital_signatures

        self.assertEqual(1, signatures.count)
        self.assertTrue(signatures.is_valid)

    # WORDSNET-13036, WORDSNET-16868
    def test_sign_document_obfuscation_bug(self):

        cert_holder = aw.digitalsignatures.CertificateHolder.create(MY_DIR + "morzal.pfx", "aw")

        doc = aw.Document(MY_DIR + "Structured document tags.docx")
        output_file_name = ARTIFACTS_DIR + "DigitalSignatureUtil.sign_document_obfuscation_bug.doc"

        sign_options = aw.digitalsignatures.SignOptions()
        sign_options.comments = "Comment"
        sign_options.sign_time = datetime.now()

        aw.digitalsignatures.DigitalSignatureUtil.sign(doc.original_file_name, output_file_name, cert_holder, sign_options)

    # WORDSNET-16868
    def test_incorrect_decryption_password(self):

        certificate_holder = aw.digitalsignatures.CertificateHolder.create(MY_DIR + "morzal.pfx", "aw")

        doc = aw.Document(MY_DIR + "Encrypted.docx", aw.loading.LoadOptions("docPassword"))
        output_file_name = ARTIFACTS_DIR + "DigitalSignatureUtil.incorrect_decryption_password.docx"

        sign_options = aw.digitalsignatures.SignOptions()
        sign_options.comments = "Comment"
        sign_options.sign_time = datetime.now()
        sign_options.decryption_password = "docPassword1"

        with self.assertRaises(Exception, msg="The document password is incorrect."):
            aw.digitalsignatures.DigitalSignatureUtil.sign(doc.original_file_name, output_file_name, certificate_holder, sign_options)

    def test_no_arguments_for_sing(self):

        sign_options = aw.digitalsignatures.SignOptions()
        sign_options.comments = ""
        sign_options.sign_time = datetime.now()
        sign_options.decryption_password = ""

        with self.assertRaises(Exception):
            aw.digitalsignatures.DigitalSignatureUtil.sign("", "", None, sign_options)

    def test_no_certificate_for_sign(self):

        doc = aw.Document(MY_DIR + "Digitally signed.docx")
        output_file_name = ARTIFACTS_DIR + "DigitalSignatureUtil.no_certificate_for_sign.docx"

        sign_options = aw.digitalsignatures.SignOptions()
        sign_options.comments = "Comment"
        sign_options.sign_time = datetime.now()
        sign_options.decryption_password = "docPassword"

        with self.assertRaises(Exception):
            aw.digitalsignatures.DigitalSignatureUtil.sign(doc.original_file_name, output_file_name, None, sign_options)
