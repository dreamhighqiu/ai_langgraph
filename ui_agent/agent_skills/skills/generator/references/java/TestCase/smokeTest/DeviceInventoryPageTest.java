package com.zebra.TestCase.smokeTest;

import com.epam.reportportal.junit5.ReportPortalExtension;
import com.zebra.helper.CommonHelper;
import com.zebra.helper.Hook;
import com.zebra.property.HarmonixProperty;
import org.junit.jupiter.api.Assumptions;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import java.util.Arrays;
import java.util.List;

@ExtendWith(ReportPortalExtension.class)
class DeviceInventoryPageTest extends Hook {
    @BeforeAll
    static void skipIfSkipModule() {
        Assumptions.assumeFalse(
                HarmonixProperty.skipModule.contains("DeviceInventoryPage".toLowerCase()),
                "Tests are skipped environment"
        );
    }

    @Test
    @Tag("smoke")
    void checkDeviceInventoryPageUI() throws InterruptedException {
        deviceInventoryHelper.verifyAllKeyElementsOnDeviceInventoryPresence();
    }

    @Test
    @Tag("smoke")
    void checkSortFunctionInDeviceInventoryPageUIForMultiField() throws InterruptedException {
        deviceInventoryHelper.verifyAllKeyElementsOnDeviceInventoryPresence();
        List<CommonHelper.SortAction> sortActions = List.of(
            new CommonHelper.SortAction("Model", "model", CommonHelper.SortDirection.ASCENDING),
            new CommonHelper.SortAction("Device Name", "name", CommonHelper.SortDirection.DESCENDING)
        );
        String apiPath = "v1/devices";
        String uniqueUiColumnHeader = "Serial Number";
        int uniqueUiColumnIndex = 5;
        String uniqueApiJsonKey = "serial_number";
        List<String> allUiColumnHeaders = List.of("Model", "Device Name", "Device Type", "Serial Number", "OS Version");
        int maxScrolls = 3;
        CommonHelper.SortVerificationSetup setup = helperContext.getCommonHelper().setupSortVerification(
            apiPath,
            sortActions
        );

        helperContext.getCommonHelper().executeAndVerifySort(
            setup,
            uniqueUiColumnHeader,
            uniqueApiJsonKey,
            allUiColumnHeaders,
            maxScrolls
        );
    }

    @Test
    @Tag("smoke")
    void checkSortDeviceNameFunctionInDeviceInventoryPageUIForOneField() throws InterruptedException {
        deviceInventoryHelper.verifyAllKeyElementsOnDeviceInventoryPresence();

        List<CommonHelper.SortAction> sortActions = List.of(
            new CommonHelper.SortAction("Device Name", "name", CommonHelper.SortDirection.DESCENDING)
        );
        String apiPath = "v1/devices";
        String uniqueUiColumnHeader = "Serial Number";
        int uniqueUiColumnIndex = 5;
        String uniqueApiJsonKey = "serial_number";
        List<String> allUiColumnHeaders = List.of("Model", "Device Name", "Device Type", "Serial Number", "OS Version");
        int maxScrolls = 3;
        CommonHelper.SortVerificationSetup setup = helperContext.getCommonHelper().setupSortVerification(
            apiPath,
            sortActions
        );

        helperContext.getCommonHelper().executeAndVerifySort(
            setup,
            uniqueUiColumnHeader,
            uniqueApiJsonKey,
            allUiColumnHeaders,
            maxScrolls
        );
    }

    @Test
    @Tag("smoke")
    void checkSortSerialNumberFunctionInDeviceInventoryPageUIForOneField() throws InterruptedException {
        deviceInventoryHelper.verifyAllKeyElementsOnDeviceInventoryPresence();

        List<CommonHelper.SortAction> sortActions = List.of(
            new CommonHelper.SortAction("Serial Number", "serial_number", CommonHelper.SortDirection.DESCENDING)
        );
        String apiPath = "v1/devices";
        String uniqueUiColumnHeader = "Serial Number";
        int uniqueUiColumnIndex = 5;
        String uniqueApiJsonKey = "serial_number";
        List<String> allUiColumnHeaders = List.of("Model", "Device Name", "Device Type", "Serial Number", "OS Version");
        int maxScrolls = 3;
        CommonHelper.SortVerificationSetup setup = helperContext.getCommonHelper().setupSortVerification(
            apiPath,
            sortActions
        );

        helperContext.getCommonHelper().executeAndVerifySort(
            setup,
            uniqueUiColumnHeader,
            uniqueApiJsonKey,
            allUiColumnHeaders,
            maxScrolls
        );

    }

    @Test
    @Tag("smoke")
    void checkSortDeviceNameAndOSVersionFunctionInDeviceInventoryPageUIForOneField() throws InterruptedException {
        deviceInventoryHelper.verifyAllKeyElementsOnDeviceInventoryPresence();

        List<CommonHelper.SortAction> sortActions = List.of(
            new CommonHelper.SortAction("Device Name", "name", CommonHelper.SortDirection.DESCENDING),
            new CommonHelper.SortAction("OS Version", "os_version.version", CommonHelper.SortDirection.ASCENDING)
        );
        String apiPath = "v1/devices";
        String uniqueUiColumnHeader = "Serial Number";
        String uniqueApiJsonKey = "serial_number";
        List<String> allUiColumnHeaders = List.of("Model", "Device Name", "Device Type", "Serial Number", "OS Version");
        int maxScrolls = 3;
        CommonHelper.SortVerificationSetup setup = helperContext.getCommonHelper().setupSortVerification(
            apiPath,
            sortActions
        );

        helperContext.getCommonHelper().executeAndVerifySort(
            setup,
            uniqueUiColumnHeader,
            uniqueApiJsonKey,
            allUiColumnHeaders,
            maxScrolls
        );
    }

    @Test
    @Tag("smoke")
    void filterModelWithOneTag () {
        commonHelper.filterWithSingleOptionAndCheckFilterResult("Model");
    }

    @Test
    @Tag("smoke")
    void filterModelWithTags () {
        commonHelper.filterWithMultipleOptionsAndCheckFilterResult("Model");
    }

    @Test
    @Tag("smoke")
    void resetModelFilter () {
        commonHelper.resetFilterAndCheckResult("Model");
    }

    @Test
    @Tag("smoke")
    void filterOSVersionWithOneTag () {
        commonHelper.filterWithSingleOptionAndCheckFilterResult("OS Version");
    }

    @Test
    @Tag("smoke")
    void filterOSVersionWithTags () {
        commonHelper.filterWithMultipleOptionsAndCheckFilterResult("OS Version");
    }

    @Test
    @Tag("smoke")
    void resetOSVersionFilter () {
        commonHelper.resetFilterAndCheckResult("OS Version");
    }

    @Test
    @Tag("smoke")
    void filterOSVersionAndModelWithOneTag () {
        List<String> OSVersions = commonHelper.filterWithSingleOptionAndCheckFilterResult("OS Version");
        List<String> models = commonHelper.filterWithSingleOptionAndCheckFilterResult("Model");
        commonHelper.checkFilterResultIsCorrectWithMultipleFilters( Arrays.asList("OS Version", "Model"));
        int resultCount = commonHelper.checkResultMatchEachFilter( Arrays.asList("OS Version", "Model"));
        commonHelper.openFilterMenu("OS Version");
        commonHelper.resetSelectedFilterAndCheckResult(OSVersions, "OS Version");
        commonHelper.openFilterMenu("Model");
        commonHelper.resetSelectedFilterAndCheckResult(models, "Model");
        commonHelper.checkAllDataLoad(resultCount);
    }

    @Test
    @Tag("smoke")
    void filterOSVersionAndModelWithTags () {
        List<String> models = commonHelper.filterWithMultipleOptionsAndCheckFilterResult("Model");
        List<String> OSVersions = commonHelper.filterWithMultipleOptionsAndCheckFilterResult("OS Version");
        commonHelper.checkFilterResultIsCorrectWithMultipleFilters( Arrays.asList("Model", "OS Version"));
        int resultCount = commonHelper.checkResultMatchEachFilter( Arrays.asList("Model", "OS Version"));
        commonHelper.openFilterMenu("Model");
        commonHelper.resetSelectedFilterAndCheckResult(models, "Model");
        commonHelper.openFilterMenu("OS Version");
        commonHelper.resetSelectedFilterAndCheckResult(OSVersions, "OS Version");
        commonHelper.checkAllDataLoad(resultCount);
    }
}

