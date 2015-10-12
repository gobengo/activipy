## Activipy --- ActivityStreams 2.0 implementation and testing for Python
## Copyright © 2015 Christopher Allan Webber <cwebber@dustycloud.org>
##
## This file is part of Activipy, which is GPLv3+ or Apache v2, your option
## (see COPYING); since that means effectively Apache v2 here's those headers
##
## Apache v2 header:
##   Licensed under the Apache License, Version 2.0 (the "License");
##   you may not use this file except in compliance with the License.
##   You may obtain a copy of the License at
##
##       http://www.apache.org/licenses/LICENSE-2.0
##
##   Unless required by applicable law or agreed to in writing, software
##   distributed under the License is distributed on an "AS IS" BASIS,
##   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##   See the License for the specific language governing permissions and
##   limitations under the License.

import copy
from activipy import types




# Fake inheritance tree below

def fake_type_uri(type_name):
    return "http://example.org/ns#" + type_name
    
ASObject = types.ASType(fake_type_uri("object"), [], "Object")
ASLink = types.ASType(fake_type_uri("link"), [], "Link")

ASActivity = types.ASType(fake_type_uri("activity"), [ASObject], "Activity")
ASPost = types.ASType(fake_type_uri("post"), [ASActivity], "Post")
ASDelete = types.ASType(fake_type_uri("delete"), [ASActivity], "Delete")

ASCollection = types.ASType(
    fake_type_uri("collection"), [ASObject], "Collection")
ASOrderedCollection = types.ASType(
    fake_type_uri("orderedcollection"),
    [ASCollection],
    "OrderedCollection")
ASCollectionPage = types.ASType(
    fake_type_uri("collectionpage"),
    [ASCollection],
    "CollectionPage")
ASOrderedCollectionPage = types.ASType(
    fake_type_uri("orderedcollectionpage"),
    [ASOrderedCollection, ASCollectionPage],
    "OrderedCollectionPage")




# Basic tests

def test_inheritance_list():
    # Should just be itself
    assert types.astype_inheritance_list(ASObject) == \
        [ASObject]
    assert types.astype_inheritance_list(ASLink) == \
        [ASLink]

    # Should be itself, then its parent
    assert types.astype_inheritance_list(ASActivity) == \
        [ASActivity, ASObject]
    assert types.astype_inheritance_list(ASCollection) == \
        [ASCollection, ASObject]

    # A slightly longer inheritance chain
    assert types.astype_inheritance_list(ASPost) == \
        [ASPost, ASActivity, ASObject]
    assert types.astype_inheritance_list(ASDelete) == \
        [ASDelete, ASActivity, ASObject]
    assert types.astype_inheritance_list(ASOrderedCollection) == \
        [ASOrderedCollection, ASCollection, ASObject]
    assert types.astype_inheritance_list(ASCollectionPage) == \
        [ASCollectionPage, ASCollection, ASObject]

    # Multiple inheritance!  Egads.
    # ... this clearly demonstrates our present depth-first
    # traversal.  A breadth-first traversal would mean
    # ASCollectionPage would go before ASCollection, which may be more
    # to a user's expectations.
    assert types.astype_inheritance_list(ASOrderedCollectionPage) == \
        [ASOrderedCollectionPage, ASOrderedCollection,
         ASCollection, ASObject, ASCollectionPage]

    # does the property version also work?
    assert ASOrderedCollectionPage.inheritance_chain == \
        [ASOrderedCollectionPage, ASOrderedCollection,
         ASCollection, ASObject, ASCollectionPage]


ROOT_BEER_NOTE_JSOBJ = {
    "@type": "Create",
    "@id": "http://tsyesika.co.uk/act/foo-id-here/",
    "actor": {
        "@type": "Person",
        "@id": "http://tsyesika.co.uk/",
        "displayName": "Jessica Tallon"},
    "to": ["acct:cwebber@identi.ca",
           "acct:justaguy@rhiaro.co.uk"],
    "object": {
        "@type": "Note",
        "@id": "htp://tsyesika.co.uk/chat/sup-yo/",
        "content": "Up for some root beer floats?"}}

ROOT_BEER_NOTE_MIXED_ASOBJ = {
    "@type": "Create",
    "@id": "http://tsyesika.co.uk/act/foo-id-here/",
    "actor": types.ASObj({
        "@type": "Person",
        "@id": "http://tsyesika.co.uk/",
        "displayName": "Jessica Tallon"}),
    "to": ["acct:cwebber@identi.ca",
           "acct:justaguy@rhiaro.co.uk"],
    "object": types.ASObj({
        "@type": "Note",
        "@id": "htp://tsyesika.co.uk/chat/sup-yo/",
        "content": "Up for some root beer floats?"})}


def test_deepcopy_jsobj():
    def looks_like_root_beer_note(jsobj):
        return (
            len(jsobj) == 5 and
            jsobj["@type"] == "Create" and
            jsobj["@id"] == "http://tsyesika.co.uk/act/foo-id-here/" and
            isinstance(jsobj["actor"], dict) and
            len(jsobj["actor"]) == 3 and
            jsobj["actor"]["@type"] == "Person" and
            jsobj["actor"]["@id"] == "http://tsyesika.co.uk/" and
            jsobj["actor"]["displayName"] == "Jessica Tallon" and
            isinstance(jsobj["to"], list) and
            jsobj["to"] == ["acct:cwebber@identi.ca",
                            "acct:justaguy@rhiaro.co.uk"] and
            isinstance(jsobj["object"], dict) and
            len(jsobj["object"]) == 3 and
            jsobj["object"]["@type"] == "Note" and
            jsobj["object"]["@id"] == "htp://tsyesika.co.uk/chat/sup-yo/" and
            jsobj["object"]["content"] == "Up for some root beer floats?")

    # We'll mutate later, so let's make a copy of this
    root_beer_note = copy.deepcopy(ROOT_BEER_NOTE_JSOBJ)
    assert looks_like_root_beer_note(root_beer_note)

    # Test copying a compicated datastructure
    copied_root_beer_note = types.deepcopy_jsobj(root_beer_note)
    assert looks_like_root_beer_note(copied_root_beer_note)

    # Mutate
    root_beer_note["to"].append("sneaky@mcsneakers.example")
    assert not looks_like_root_beer_note(root_beer_note)
    # but things are still as they were in our copy right??
    assert looks_like_root_beer_note(copied_root_beer_note)

    # Test nested asobj copying
    assert looks_like_root_beer_note(
        types.deepcopy_jsobj(ROOT_BEER_NOTE_MIXED_ASOBJ))


ROOT_BEER_NOTE_ASOBJ = types.ASObj({
    "@type": "Create",
    "@id": "http://tsyesika.co.uk/act/foo-id-here/",
    "actor": types.ASObj({
        "@type": "Person",
        "@id": "http://tsyesika.co.uk/",
        "displayName": "Jessica Tallon"}),
    "to": ["acct:cwebber@identi.ca",
           "acct:justaguy@rhiaro.co.uk"],
    "object": types.ASObj({
        "@type": "Note",
        "@id": "htp://tsyesika.co.uk/chat/sup-yo/",
        "content": "Up for some root beer floats?"})})


def test_asobj_keyaccess():
    assert ROOT_BEER_NOTE_ASOBJ["@type"] == "Create"
    assert ROOT_BEER_NOTE_ASOBJ["@id"] == \
        "http://tsyesika.co.uk/act/foo-id-here/"

    # Accessing things that look like asobjects
    # will return asobjects
    assert isinstance(
        ROOT_BEER_NOTE_ASOBJ["object"],
        types.ASObj)

    # However, we should still be able to get the
    # dictionary edition by pulling down .json()
    assert isinstance(
        ROOT_BEER_NOTE_ASOBJ.json()["object"],
        dict)

    # Traversal of traversal should work
    assert ROOT_BEER_NOTE_ASOBJ["object"]["content"] == \
        "Up for some root beer floats?"