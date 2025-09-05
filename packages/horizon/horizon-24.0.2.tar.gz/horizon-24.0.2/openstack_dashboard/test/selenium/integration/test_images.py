#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os
import tempfile
import time

import pytest

from oslo_utils import uuidutils

from openstack_dashboard.test.selenium import widgets


@pytest.fixture(params=[1])
def image_names(request):
    count = request.param
    img_name_list = ['horizon_img_%s' % uuidutils.generate_uuid(dashed=False)]
    if count > 1:
        img_name_list = [f"{img_name_list[0]}-{item}"
                         for item in range(1, count + 1)]
    return img_name_list


@pytest.fixture
def new_image_demo(image_names, temporary_file, openstack_demo):
    for img in image_names:
        image = openstack_demo.create_image(
            img,
            disk_format="qcow2",
            filename=temporary_file,
            wait=True,
        )
    yield image
    for img in image_names:
        openstack_demo.delete_image(img)


@pytest.fixture
def new_image_admin(image_names, temporary_file, openstack_admin):
    for img in image_names:
        image = openstack_admin.create_image(
            img,
            disk_format="qcow2",
            filename=temporary_file,
            wait=True,
        )
    yield image
    for img in image_names:
        openstack_admin.delete_image(img)


@pytest.fixture
def new_protected_image_admin(image_names, temporary_file, openstack_admin):
    for img in image_names:
        image = openstack_admin.create_image(
            img,
            disk_format="qcow2",
            filename=temporary_file,
            is_protected=True,
            wait=True,
        )
    yield image
    for img in image_names:
        openstack_admin.delete_image(img)


@pytest.fixture
def clear_image_demo(image_names, openstack_demo):
    yield None
    for img in image_names:
        openstack_demo.delete_image(
            img,
            wait=True,
        )


@pytest.fixture
def clear_image_admin(image_names, openstack_admin):
    yield None
    for img in image_names:
        openstack_admin.delete_image(
            img,
            wait=True,
        )


@pytest.fixture
def temporary_file(tmp_path):
    """Generate temporary file.

    :return: path to the generated file
    """
    with tempfile.NamedTemporaryFile(suffix='.qcow2',
                                     dir=tmp_path) as tmp_file:
        tmp_file.write(os.urandom(5000))
        yield tmp_file.name


def wait_for_steady_state_of_unprotected_image(openstack, image_name):
    for attempt in range(3):
        image_attributes_details = openstack.image.find_image(image_name)
        if image_attributes_details["status"] == "active" \
                and image_attributes_details["protected"] is False:
            break
        else:
            time.sleep(2)


def wait_for_angular_readiness(driver):
    driver.set_script_timeout(10)
    driver.execute_async_script("""
    var callback = arguments[arguments.length - 1];
    var element = document.querySelector('div.btn-group[name="protected"]');
    if (!window.angular) {
    callback(false)
    }
    if (angular.getTestability) {
    angular.getTestability(element).whenStable(function(){callback(true)});
    } else {
    if (!angular.element(element).injector()) {
    callback(false)
    }
    var browser = angular.element(element).injector().get('$browser');
    browser.notifyWhenNoOutstandingRequests(function(){callback(true)});
    };""")


def test_image_create_from_local_file_demo(login, driver, image_names,
                                           temporary_file, clear_image_demo,
                                           config, openstack_demo):
    image_name = image_names[0]
    login('user', 'demo')
    url = '/'.join((
        config.dashboard.dashboard_url,
        'project',
        'images',
    ))
    driver.get(url)
    driver.find_element_by_xpath(
        "//button[normalize-space()='Create Image']").click()
    wizard = driver.find_element_by_css_selector("wizard")
    wizard.find_element_by_id("imageForm-name").send_keys(image_name)
    select_element = wizard.find_element_by_css_selector(
        "input[name='image_file']")
    select_element.send_keys(temporary_file)
    wizard.find_element_by_id("imageForm-format").click()
    wizard.find_element_by_css_selector(
        "[label='QCOW2 - QEMU Emulator']").click()
    wizard.find_element_by_css_selector("button.btn-primary.finish").click()
    messages = widgets.get_and_dismiss_messages(driver)
    assert(f"Success: Image {image_name} was successfully"
           f" created." in messages)
    assert openstack_demo.compute.find_image(image_name) is not None


def test_image_delete_demo(login, driver, image_names, openstack_demo,
                           new_image_demo, config):
    image_name = image_names[0]
    login('user', 'demo')
    url = '/'.join((
        config.dashboard.dashboard_url,
        'project',
        'images',
    ))
    driver.get(url)
    rows = driver.find_elements_by_xpath(f"//a[text()='{image_name}']")
    assert len(rows) == 1
    actions_column = rows[0].find_element_by_xpath(
        ".//ancestor::tr/td[contains(@class,'actions_column')]")
    widgets.select_from_dropdown(actions_column, "Delete Image")
    widgets.confirm_modal(driver)
    messages = widgets.get_and_dismiss_messages(driver)
    assert f"Success: Deleted Image: {image_name}." in messages
    assert openstack_demo.compute.find_image(image_name) is None


@pytest.mark.parametrize('image_names', [2], indirect=True)
def test_image_pagination_demo(login, driver, image_names, openstack_demo,
                               change_page_size_demo, new_image_demo, config):
    items_per_page = 1
    img_list = sorted([item["name"]
                       for item in openstack_demo.compute.images()])
    first_page_definition = widgets.TableDefinition(next=True, prev=False,
                                                    count=items_per_page,
                                                    names=[img_list[0]])
    second_page_definition = widgets.TableDefinition(next=True, prev=True,
                                                     count=items_per_page,
                                                     names=[img_list[1]])
    third_page_definition = widgets.TableDefinition(next=False, prev=True,
                                                    count=items_per_page,
                                                    names=[img_list[2]])
    login('user', 'demo')
    url = '/'.join((
        config.dashboard.dashboard_url,
        'project',
        'images',
    ))
    driver.get(url)
    actual_page1_definition = widgets.get_image_table_definition(driver,
                                                                 sorting=True)
    assert first_page_definition == actual_page1_definition
    # Turning to next page(page2)
    driver.find_element_by_link_text("Next »").click()
    actual_page2_definition = widgets.get_image_table_definition(driver,
                                                                 sorting=True)
    assert second_page_definition == actual_page2_definition
    # Turning to next page(page3)
    driver.find_element_by_link_text("Next »").click()
    actual_page3_definition = widgets.get_image_table_definition(driver,
                                                                 sorting=True)
    assert third_page_definition == actual_page3_definition
    # Turning back to previous page(page2)
    driver.find_element_by_link_text("« Prev").click()
    actual_page2_definition = widgets.get_image_table_definition(driver,
                                                                 sorting=True)
    assert second_page_definition == actual_page2_definition
    # Turning back to previous page(page1)
    driver.find_element_by_link_text("« Prev").click()
    actual_page1_definition = widgets.get_image_table_definition(driver,
                                                                 sorting=True)
    assert first_page_definition == actual_page1_definition


# Admin tests


def test_image_create_from_local_file_admin(login, driver, image_names,
                                            temporary_file, clear_image_admin,
                                            config, openstack_admin):
    image_name = image_names[0]
    login('admin', 'admin')
    url = '/'.join((
        config.dashboard.dashboard_url,
        'project',
        'images',
    ))
    driver.get(url)
    driver.find_element_by_xpath(
        "//button[normalize-space()='Create Image']").click()
    wizard = driver.find_element_by_css_selector("wizard")
    wizard.find_element_by_id("imageForm-name").send_keys(image_name)
    select_element = wizard.find_element_by_css_selector(
        "input[name='image_file']")
    select_element.send_keys(temporary_file)
    wizard.find_element_by_id("imageForm-format").click()
    wizard.find_element_by_css_selector(
        "[label='QCOW2 - QEMU Emulator']").click()
    wizard.find_element_by_css_selector("button.btn-primary.finish").click()
    messages = widgets.get_and_dismiss_messages(driver)
    assert(f"Success: Image {image_name} was successfully"
           f" created." in messages)
    assert openstack_admin.compute.find_image(image_name) is not None


def test_image_delete_admin(login, driver, image_names, openstack_admin,
                            new_image_admin, config):
    image_name = image_names[0]
    login('admin', 'admin')
    url = '/'.join((
        config.dashboard.dashboard_url,
        'project',
        'images',
    ))
    driver.get(url)
    rows = driver.find_elements_by_xpath(f"//a[text()='{image_name}']")
    assert len(rows) == 1
    actions_column = rows[0].find_element_by_xpath(
        ".//ancestor::tr/td[contains(@class,'actions_column')]")
    widgets.select_from_dropdown(actions_column, "Delete Image")
    widgets.confirm_modal(driver)
    messages = widgets.get_and_dismiss_messages(driver)
    assert f"Success: Deleted Image: {image_name}." in messages
    assert openstack_admin.compute.find_image(image_name) is None


@pytest.mark.parametrize('image_names', [2], indirect=True)
def test_image_pagination_admin(login, driver, image_names, openstack_admin,
                                change_page_size_admin, new_image_admin,
                                config):
    items_per_page = 1
    img_list = sorted([item["name"]
                       for item in openstack_admin.compute.images()])
    first_page_definition = widgets.TableDefinition(next=True, prev=False,
                                                    count=items_per_page,
                                                    names=[img_list[0]])
    second_page_definition = widgets.TableDefinition(next=True, prev=True,
                                                     count=items_per_page,
                                                     names=[img_list[1]])
    third_page_definition = widgets.TableDefinition(next=False, prev=True,
                                                    count=items_per_page,
                                                    names=[img_list[2]])
    login('admin', 'admin')
    url = '/'.join((
        config.dashboard.dashboard_url,
        'project',
        'images',
    ))
    driver.get(url)
    actual_page1_definition = widgets.get_image_table_definition(driver,
                                                                 sorting=True)
    assert first_page_definition == actual_page1_definition
    # Turning to next page(page2)
    driver.find_element_by_link_text("Next »").click()
    actual_page2_definition = widgets.get_image_table_definition(driver,
                                                                 sorting=True)
    assert second_page_definition == actual_page2_definition
    # Turning to next page(page3)
    driver.find_element_by_link_text("Next »").click()
    actual_page3_definition = widgets.get_image_table_definition(driver,
                                                                 sorting=True)
    assert third_page_definition == actual_page3_definition
    # Turning back to previous page(page2)
    driver.find_element_by_link_text("« Prev").click()
    actual_page2_definition = widgets.get_image_table_definition(driver,
                                                                 sorting=True)
    assert second_page_definition == actual_page2_definition
    # Turning back to previous page(page1)
    driver.find_element_by_link_text("« Prev").click()
    actual_page1_definition = widgets.get_image_table_definition(driver,
                                                                 sorting=True)
    assert first_page_definition == actual_page1_definition


def test_image_filtration_admin(login, driver, new_image_admin, config):
    image_name = new_image_admin.name
    login('admin', 'admin')
    url = '/'.join((
        config.dashboard.dashboard_url,
        'project',
        'images',
    ))
    driver.get(url)
    filter_input_field = driver.find_element_by_css_selector(".search-input")
    filter_input_field.send_keys(image_name)
    # Fetch page definition after filtration
    current_page_definition = widgets.get_image_table_definition(driver)
    assert vars(current_page_definition)['names'][0] == image_name
    assert vars(current_page_definition)['count'] == 1
    filter_input_field.clear()
    # Generate random non existent image name
    random_img_name = 'horizon_img_%s' % uuidutils.generate_uuid(dashed=False)
    filter_input_field.send_keys(random_img_name)
    # Fetch page definition after filtration
    current_page_definition = widgets.get_image_table_definition(driver)
    assert current_page_definition is None


def test_remove_protected_image_admin(login, driver, image_names,
                                      new_protected_image_admin, config,
                                      openstack_admin):
    image_name = new_protected_image_admin.name
    login('admin', 'admin')
    url = '/'.join((
        config.dashboard.dashboard_url,
        'project',
        'images',
    ))
    driver.get(url)
    rows = driver.find_elements_by_xpath(f"//a[text()='{image_name}']")
    assert len(rows) == 1
    actions_column = rows[0].find_element_by_xpath(
        ".//ancestor::tr/td[contains(@class,'actions_column')]")
    menu_button = actions_column.find_element_by_css_selector(
        ".dropdown-toggle"
    )
    menu_button.click()
    options = actions_column.find_elements_by_css_selector(
        "ul.dropdown-menu li")
    for option in options:
        if option.text == "Delete Image":
            pytest.fail("Delete option should not exist")
    actions_column.find_element_by_xpath(
        f".//*[normalize-space()='Edit Image']").click()
    wait_for_angular_readiness(driver)
    image_form = driver.find_element_by_css_selector(".ng-wizard")
    image_form.find_element_by_xpath(".//label[text()='No']").click()
    image_form.find_element_by_xpath(
        ".//button[@class='btn btn-primary finish']").click()
    messages = widgets.get_and_dismiss_messages(driver)
    assert f"Success: Image {image_name} was successfully updated." in messages
    wait_for_steady_state_of_unprotected_image(openstack_admin, image_name)
    rows = driver.find_elements_by_xpath(f"//a[text()='{image_name}']")
    actions_column = rows[0].find_element_by_xpath(
        ".//ancestor::tr/td[contains(@class,'actions_column')]")
    widgets.select_from_dropdown(actions_column, "Delete Image")
    widgets.confirm_modal(driver)
    messages = widgets.get_and_dismiss_messages(driver)
    assert f"Success: Deleted Image: {image_name}." in messages
    assert openstack_admin.compute.find_image(image_name) is None


def test_edit_image_description_admin(login, driver, image_names,
                                      new_image_admin, config,
                                      openstack_admin):
    image_name = new_image_admin.name
    new_description = "new_description_text"
    login('admin', 'admin')
    url = '/'.join((
        config.dashboard.dashboard_url,
        'project',
        'images',
    ))
    driver.get(url)
    rows = driver.find_elements_by_xpath(f"//a[text()='{image_name}']")
    assert len(rows) == 1
    actions_column = rows[0].find_element_by_xpath(
        ".//ancestor::tr/td[contains(@class,'actions_column')]")
    widgets.select_from_dropdown(actions_column, "Edit Image")
    wait_for_angular_readiness(driver)
    image_form = driver.find_element_by_css_selector(".ng-wizard")
    desc_field = image_form.find_element_by_css_selector(
        "#imageForm-description")

    desc_field.clear()
    desc_field.send_keys(new_description)
    image_form.find_element_by_xpath(
        ".//button[@class='btn btn-primary finish']").click()
    messages = widgets.get_and_dismiss_messages(driver)
    assert f"Success: Image {image_name} " \
           f"was successfully updated." in messages
    image_id = new_image_admin.id
    assert (openstack_admin.compute.get(f"/images/{image_id}").json(
    )['image']['metadata']['description'] == new_description)
