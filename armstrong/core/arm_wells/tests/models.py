import datetime
import random

from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

from ._utils import (TestCase, add_n_random_stories_to_well,
        generate_random_well, generate_random_welltype, generate_random_story)

from ..models import WellType, Well, Node
from .arm_wells_support.models import (MissingFieldWell, MissingFieldWellNode,
        Story, NewWell, NewNode, DifferentWell, DifferentWellType,
        WrongRelationWell, WrongRelationNode)


#
# Abstract BaseModel tests
#

class BaseWellTestCase(TestCase):
    def test_missing_type_field(self):
        well = MissingFieldWell()
        with self.assertRaises(NotImplementedError):
            well.type

        well = MissingFieldWell.objects.create()
        with self.assertRaises(NotImplementedError):
            well.type

    def test_has_type_field(self):
        well = Well()
        with self.assertRaises(ObjectDoesNotExist):
            well.type

        with self.assertRaises(IntegrityError):
            Well.objects.create()

        well = Well.objects.create(type=generate_random_welltype())
        self.assertEqual(WellType, type(well.type))


class BaseWellNodeTestCase(TestCase):
    def test_missing_well_field(self):
        node = MissingFieldWellNode()
        with self.assertRaises(NotImplementedError):
            node.well

        with self.assertRaises(IntegrityError):
            MissingFieldWellNode.objects.create()

    def test_has_well_field(self):
        node = Node()
        with self.assertRaises(ObjectDoesNotExist):
            node.well

        with self.assertRaises(IntegrityError):
            Node.objects.create(content_object=generate_random_story(),
                                order=100)

        node = Node.objects.create(content_object=generate_random_story(),
                                   well=generate_random_well(),
                                   order=100)
        self.assertEqual(Well, type(node.well))


class SubclassesTestCase(TestCase):
    def setUp(self):
        self.well = NewWell.objects.create(type=generate_random_welltype())
        self.node1 = NewNode.objects.create(
                content_object=generate_random_story(), well=self.well,
                order=100)

        self.node2 = NewNode.objects.create(
                content_object=generate_random_story(), well=self.well,
                order=9)

    def test_has_correct_relations(self):
        self.assertEqual(WellType, type(self.well.type))
        self.assertEqual(NewWell, type(self.node1.well))
        self.assertEqual(NewWell, type(self.node2.well))
        self.assertEqual(NewNode, type(self.node1))
        self.assertEqual(NewNode, type(self.node2))

    def test_has_wrong_relations(self):
        dwt = DifferentWellType.objects.create(title="title", slug="slug")
        dw = DifferentWell.objects.create(type=dwt)
        self.assertEqual(DifferentWellType, type(dw.type))

        with self.assertRaises(ValueError):
            # NewNode relates to NewWell
            NewNode.objects.create(
                content_object=generate_random_story(),
                well=generate_random_well(),
                order=1
            )
        with self.assertRaises(ValueError):
            # DifferentWell relates to DifferentWellType
            DifferentWell.objects.create(type=generate_random_welltype())

    def test_has_working_items_relation(self):
        # make sure 'items' works
        self.assertEqual(2, self.well.items.count())

        # make sure related_name 'nodes' works
        self.assertEqual(self.well.items.count(),
                         self.well.nodes.count())

        # make sure content is the same
        self.assertEqual(self.well.nodes.all()[0], self.node2)
        self.assertEqual(self.well.nodes.all()[1], self.node1)
        self.assertEqual(self.well.items[0],
                         self.well.nodes.all()[0].content_object)
        self.assertEqual(self.well.items[1],
                         self.well.nodes.all()[1].content_object)

    def test_has_broken_items_relation(self):
        well = WrongRelationWell.objects.create(
                type=generate_random_welltype())
        node = WrongRelationNode.objects.create(
                content_object=generate_random_story(), well=well, order=1)

        with self.assertRaises(AttributeError):
            well.items
        with self.assertRaises(AttributeError):
            well.nodes

        self.assertEqual(1, well.foo.count())
        self.assertEqual(node, well.foo.all()[0])


#
# Concrete Model tests
#

class WellTestCase(TestCase):
    def test_has_as_many_nodes_as_are_added(self):
        well = generate_random_well()
        self.assertEqual(0, well.nodes.count(), msg="Sanity check")

        r = random.randint(1, 10)
        for i in range(r):
            Node.objects.create(well=well,
                    content_object=generate_random_story())

        self.assertEqual(r, well.nodes.count())

    def test_nodes_are_sorted_by_order(self):
        well = generate_random_well()
        second = Node.objects.create(well=well,
                content_object=generate_random_story(), order=100)
        first = Node.objects.create(well=well,
                content_object=generate_random_story(), order=10)

        self.assertEqual(first, well.nodes.all()[0])
        self.assertEqual(second, well.nodes.all()[1])

    def test_outputs_title_and_pub_date_when_cast_to_string(self):
        title = "some-random-title-%d" % random.randint(10, 100)
        date = datetime.datetime.now()

        type = WellType.objects.create(title=title, slug=title)
        well = Well.objects.create(type=type, pub_date=date)
        self.assertEqual("%s (%s - Never)" % (title, date), str(well))

    def test_outputs_expires_if_present(self):
        title = "some-random-title-%d" % random.randint(10, 100)
        date = datetime.datetime.now()

        type = WellType.objects.create(title=title, slug=title)
        well = Well.objects.create(type=type, pub_date=date, expires=date)
        self.assertEqual("%s (%s - %s)" % (title, date, date), str(well))

    def test_combines_a_well_with_another_queryset(self):
        number_of_stories = random.randint(1, 5)
        for i in range(number_of_stories):
            generate_random_story()

        well = generate_random_well()
        number_in_well = random.randint(1, 5)
        add_n_random_stories_to_well(number_in_well, well)

        queryset_backed_well = well.merge_with(Story.objects.all())
        self.assertEqual(number_in_well + number_of_stories,
                len(queryset_backed_well))

    def test_title_is_the_same_as_welltype_title(self):
        well_type = generate_random_welltype()
        well = Well.objects.create(type=well_type)
        self.assertEqual(well_type.title, well.title)

    def test_well_is_iterable(self):
        well = generate_random_well()
        number_in_well = random.randint(1, 5)
        add_n_random_stories_to_well(number_in_well, well)
        i = 0
        for story in well.items:
            i = i + 1
        self.assertEqual(i, number_in_well)

    def test_well_is_iterable_with_merged_queryset(self):
        number_of_stories = random.randint(1, 5)
        for i in range(number_of_stories):
            generate_random_story()

        well = generate_random_well()
        number_in_well = random.randint(1, 5)
        add_n_random_stories_to_well(number_in_well, well)

        well.merge_with(Story.objects.all())
        i = 0
        for story in well.items:
            i = i + 1
        self.assertEqual(i, number_in_well + number_of_stories)

    def test_well_supports_indexing(self):
        well = generate_random_well()
        number_in_well = random.randint(1, 5)
        add_n_random_stories_to_well(number_in_well, well)
        i = 0
        for node in well.nodes.all():
            self.assertEqual(node.content_object, well.items[i])
            i = i + 1
        self.assertRaises(IndexError, lambda:well.items[i])

    def test_well_supports_indexing_with_merged_queryset(self):
        number_of_stories = random.randint(1, 5)
        for i in range(number_of_stories):
            generate_random_story()

        well = generate_random_well()
        number_in_well = random.randint(1, 5)
        add_n_random_stories_to_well(number_in_well, well)
        qs = Story.objects.all()
        well.merge_with(qs)
        i = 0
        # querysets are filtered to prevent duplicate objects, so we need to
        # keep track of the objects we've already seen
        used_objects = {}
        for node in well.nodes.all():
            self.assertEqual(node.content_object, well.items[i])
            used_objects[node.content_object.id] = 1
            i = i + 1
        for story in qs:
            if story.id in used_objects:
                continue
            self.assertEqual(story, well.items[i])
            i = i + 1
        self.assertRaises(IndexError, lambda:well.items[i])


class NodeTestCase(TestCase):
    def test_string_representation(self):
        story = generate_random_story()
        well = generate_random_well()
        order = random.randint(100, 200)
        node = Node.objects.create(well=well, content_object=story,
                order=order)

        expected = "%s (%d): %s" % (well.title, order, story.title)
        self.assertEqual(expected, str(node))
