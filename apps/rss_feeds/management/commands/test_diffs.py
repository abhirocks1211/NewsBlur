# encoding: utf-8
from django.core.management.base import BaseCommand
# from optparse import make_option
from utils.story_functions import htmldiff__tree
from utils.story_functions import htmldiff__mitsuhiko
from utils.story_functions import htmldiff__lxml


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        # make_option('-V', '--verbose', action='store_true',
        #     dest='verbose', default=False, help='Verbose output.'),
    )

    def handle(self, *args, **options):
        text0_old = """This is a basic test."""
        text0_new = """This is a basic test."""
        
        text1_old = """This test is basic."""
        text1_new = """This test is semi-basic."""
        
        text2_old = """Some analyst predicted last week that Apple will sell <a href="http://old.com">watches</a> “priced at several thousand dollars”"""
        text2_new = """Some analyst predicted this week that Apple will sell <a href="http://new.com">swatches</a> “priced at several thousand dollars”"""
        
        text3_old = """Testing spaces around links: <a href="http://link.com">watches</a>."""
        text3_new = """Testing spaces around links: <a href="http://link.com">swatches</a>."""
        
        text4_old = """Testing spaces between colons: <a href="http://link.com">watches</a>."""
        text4_new = """Testing spaces before colons: <a href="http://link.com">watches</a>."""
        
        print "========================================================="
        print htmldiff__tree(text0_old, text0_new)
        print htmldiff__mitsuhiko(text0_old, text0_new)
        print htmldiff__lxml(text0_old, text0_new)
        print "========================================================="
        print htmldiff__tree(text1_old, text1_new)
        print htmldiff__mitsuhiko(text1_old, text1_new)
        print htmldiff__lxml(text1_old, text1_new)
        print "========================================================="
        print htmldiff__tree(text2_old, text2_new)
        print htmldiff__mitsuhiko(text2_old, text2_new)
        print htmldiff__lxml(text2_old, text2_new)
        print "========================================================="
        print htmldiff__tree(text3_old, text3_new)
        print htmldiff__mitsuhiko(text3_old, text3_new)
        print htmldiff__lxml(text3_old, text3_new)
        print "========================================================="
        print htmldiff__tree(text4_old, text4_new)
        print htmldiff__mitsuhiko(text4_old, text4_new)
        print htmldiff__lxml(text4_old, text4_new)
        
        