# Firmware Comparison (ATmega328P)

## Comparing Codes

- http://localhost:8000/api/v1/compare-code

```json
{
  "old_code": "; =============================\n; Firmware v1 - LED Blink\n; =============================\n; Target: ATmega328P\n; Function: Blink LED on PB0\n; Author: Example Firmware\n; Date: 2025-08-28\n; =============================\n\n.include 'm328pdef.inc'\n\n; Define stack\nldi r16, low(RAMEND)\nout SPL, r16\nldi r16, high(RAMEND)\nout SPH, r16\n\n; Set PB0 as output\nldi r16, (1<<PB0)\nout DDRB, r16\n\nmain:\n ; Turn LED ON\n sbi PORTB, PB0 \n\n ; Delay loop\n ldi r18, 0xFF\n ldi r19, 0xFF\ndelay1:\n sbiw r18, 1\n brne delay1\n\n ; Turn LED OFF\n cbi PORTB, PB0 \n\n ; Delay loop\n ldi r18, 0xFF\n ldi r19, 0xFF\ndelay2:\n sbiw r18, 1\n brne delay2\n\n rjmp main",
  "new_code": "; =============================\n; Firmware v2 - LED Blink (Timer-based)\n; =============================\n; Target: ATmega328P\n; Function: Blink LED on PB0 using Timer0\n; Author: Example Firmware\n; Date: 2025-08-28\n; =============================\n\n.include 'm328pdef.inc'\n\n; Define stack\nldi r16, low(RAMEND)\nout SPL, r16\nldi r16, high(RAMEND)\nout SPH, r16\n\n; Set PB0 as output\nldi r16, (1<<PB0)\nout DDRB, r16\n\n; Setup Timer0\nldi r16, (1<<CS02) ; Prescaler 256\nout TCCR0B, r16\n\nmain:\n in r17, TCNT0 ; Read timer counter\n cpi r17, 128 ; Compare with threshold\n brne main ; If not reached, loop\n\n ; Toggle LED\n in r18, PORTB\n eor r18, (1<<PB0)\n out PORTB, r18\n\n ; Reset timer\n ldi r16, 0x00\n out TCNT0, r16\n\n rjmp main",
  "firmware_type": "ATmega328P"
}
```

---

### Output

```json
{
  "success": true,
  "differences": [
    {
      "line_number": 1,
      "change_type": "modified",
      "old_content": "; Firmware v1 - LED Blink",
      "new_content": "; Firmware v2 - LED Blink (Timer-based)",
      "context": "Version and functionality of the firmware was updated."
    },
    {
      "line_number": 17,
      "change_type": "removed",
      "old_content": "; Turn LED ON",
      "new_content": null,
      "context": "LED control and delay loop was removed."
    },
    {
      "line_number": 24,
      "change_type": "removed",
      "old_content": "; Turn LED OFF",
      "new_content": null,
      "context": "LED control and delay loop was removed."
    },
    {
      "line_number": 17,
      "change_type": "added",
      "old_content": null,
      "new_content": "; Setup Timer0",
      "context": "Timer0 setup was added."
    },
    {
      "line_number": 20,
      "change_type": "added",
      "old_content": null,
      "new_content": "in r17, TCNT0 ; Read timer counter",
      "context": "Timer counter reading was added."
    },
    {
      "line_number": 24,
      "change_type": "added",
      "old_content": null,
      "new_content": "; Reset timer",
      "context": "Timer reset was added."
    }
  ],
  "security_findings": [],
  "risk_assessment": "low",
  "change_summary": {
    "total_changes": 6,
    "major_changes": [
      "LED control and delay loop was removed.",
      "Timer0 setup, timer counter reading, and timer reset was added."
    ],
    "security_impact": "No security impact was found."
  },
  "recommendations": ["No recommendations as no security issues were found."],
  "analysis_metadata": {
    "old_code_lines": 43,
    "new_code_lines": 40,
    "total_differences": 6,
    "security_findings_count": 0,
    "analysis_method": "llm_based",
    "analysis_depth": "detailed",
    "firmware_type": "ATmega328P"
  }
}
```

## Comparing Specs

- http://localhost:8000/api/v1/compare-specs

```json
{
  "old_spec": "# LED Blink Firmware Specification v1.0\n\nTarget MCU: ATmega328P \nPin Used: PB0 (Arduino digital pin 8) \nBehavior: Blinks an LED using a software delay loop.\n\n## Implementation Notes\n\n- Uses a software delay loop with registers r18 and r19.\n- Stack is initialized at reset.\n- Main loop toggles the LED ON and OFF indefinitely.\n",
  "new_spec": "# Specification v2\n\n- Target MCU: ATmega328P\n- Pin Used: PB0\n- Behavior: The LED connected to PB0 blinks using the Timer0 hardware counter.\n\n## Key Differences from v1\n\n- Manual delay loop replaced with hardware Timer0 for timing.\n- LED toggling now uses the EOR (exclusive OR) instruction instead of SBI/CBI.\n- Improved CPU efficiency by offloading timing to hardware.\n\n## Analysis Notes (for firmware diffing exercises)\n\n- Structural Change: Delay loop replaced by timer-based wait.\n- Instruction Change: SBI/CBI replaced by EOR for toggling.\n- Specification Change: Timer usage introduced, resulting in more efficient firmware.\n"
}
```

### Output

```json
{
  "success": true,
  "differences": [
    {
      "section": "Behavior",
      "change_type": "modified",
      "old_content": "Blinks an LED using a software delay loop.",
      "new_content": "The LED connected to PB0 blinks using the Timer0 hardware counter.",
      "description": "The method of blinking the LED has changed from a software delay loop to using a hardware timer."
    },
    {
      "section": "Implementation Notes",
      "change_type": "removed",
      "old_content": "Uses a software delay loop with registers r18 and r19.",
      "new_content": null,
      "description": "The use of a software delay loop with registers r18 and r19 has been removed."
    },
    {
      "section": "Key Differences from v1",
      "change_type": "added",
      "old_content": null,
      "new_content": "Manual delay loop replaced with hardware Timer0 for timing.",
      "description": "A new section has been added to highlight key differences from the previous version. One of the key differences is the replacement of the manual delay loop with a hardware timer."
    }
  ],
  "new_features": [
    {
      "feature": "Hardware Timer0",
      "description": "The LED blinking is now controlled by a hardware timer instead of a software delay loop.",
      "impact": "This change improves CPU efficiency by offloading timing to hardware."
    },
    {
      "feature": "EOR Instruction",
      "description": "The LED toggling now uses the EOR (exclusive OR) instruction instead of SBI/CBI.",
      "impact": "This change simplifies the toggling process and potentially improves performance."
    }
  ],
  "removed_features": [
    {
      "feature": "Software Delay Loop",
      "description": "The software delay loop with registers r18 and r19 has been removed.",
      "impact": "This change could potentially improve performance and efficiency by offloading timing to hardware."
    }
  ],
  "behavioral_changes": [
    {
      "change": "LED Blinking Method",
      "old_behavior": "The LED was blinked using a software delay loop.",
      "new_behavior": "The LED is now blinked using a hardware timer.",
      "security_impact": "No direct security impact."
    }
  ],
  "change_summary": {
    "total_changes": 3,
    "major_changes": [
      "Replacement of software delay loop with hardware timer",
      "Introduction of EOR instruction for LED toggling"
    ],
    "risk_level": "low"
  },
  "recommendations": [
    "Ensure compatibility with hardware Timer0",
    "Test the new EOR instruction for LED toggling"
  ],
  "analysis_metadata": {
    "old_spec_length": 326,
    "new_spec_length": 631,
    "total_differences": 3,
    "new_features_count": 2,
    "removed_features_count": 1,
    "behavioral_changes_count": 1,
    "analysis_method": "llm_based"
  }
}
```

## Validating Compliance

- http://localhost:8000/api/v1/validate-compliance

```json
{
  "code_analysis": {
    "success": true,
    "differences": [
      {
        "line_number": 1,
        "change_type": "modified",
        "old_content": "; Firmware v1 - LED Blink",
        "new_content": "; Firmware v2 - LED Blink (Timer-based)",
        "context": "Version and functionality of the firmware was updated."
      },
      {
        "line_number": 17,
        "change_type": "removed",
        "old_content": "; Turn LED ON",
        "new_content": null,
        "context": "LED control and delay loop was removed."
      },
      {
        "line_number": 24,
        "change_type": "removed",
        "old_content": "; Turn LED OFF",
        "new_content": null,
        "context": "LED control and delay loop was removed."
      },
      {
        "line_number": 17,
        "change_type": "added",
        "old_content": null,
        "new_content": "; Setup Timer0",
        "context": "Timer0 setup was added."
      },
      {
        "line_number": 20,
        "change_type": "added",
        "old_content": null,
        "new_content": "in r17, TCNT0 ; Read timer counter",
        "context": "Timer counter reading was added."
      },
      {
        "line_number": 24,
        "change_type": "added",
        "old_content": null,
        "new_content": "; Reset timer",
        "context": "Timer reset was added."
      }
    ],
    "security_findings": [],
    "risk_assessment": "low",
    "change_summary": {
      "total_changes": 6,
      "major_changes": [
        "LED control and delay loop was removed.",
        "Timer0 setup, timer counter reading, and timer reset was added."
      ],
      "security_impact": "No security impact was found."
    },
    "recommendations": ["No recommendations as no security issues were found."],
    "analysis_metadata": {
      "old_code_lines": 43,
      "new_code_lines": 40,
      "total_differences": 6,
      "security_findings_count": 0,
      "analysis_method": "llm_based",
      "analysis_depth": "detailed",
      "firmware_type": "ATmega328P"
    }
  },
  "spec_analysis": {
    "success": true,
    "differences": [
      {
        "section": "Behavior",
        "change_type": "modified",
        "old_content": "Blinks an LED using a software delay loop.",
        "new_content": "The LED connected to PB0 blinks using the Timer0 hardware counter.",
        "description": "The method of blinking the LED has changed from a software delay loop to using a hardware timer."
      },
      {
        "section": "Implementation Notes",
        "change_type": "removed",
        "old_content": "Uses a software delay loop with registers r18 and r19.",
        "new_content": null,
        "description": "The use of a software delay loop with registers r18 and r19 has been removed."
      },
      {
        "section": "Key Differences from v1",
        "change_type": "added",
        "old_content": null,
        "new_content": "Manual delay loop replaced with hardware Timer0 for timing.",
        "description": "A new section has been added to highlight key differences from the previous version. One of the key differences is the replacement of the manual delay loop with a hardware timer."
      }
    ],
    "new_features": [
      {
        "feature": "Hardware Timer0",
        "description": "The LED blinking is now controlled by a hardware timer instead of a software delay loop.",
        "impact": "This change improves CPU efficiency by offloading timing to hardware."
      },
      {
        "feature": "EOR Instruction",
        "description": "The LED toggling now uses the EOR (exclusive OR) instruction instead of SBI/CBI.",
        "impact": "This change simplifies the toggling process and potentially improves performance."
      }
    ],
    "removed_features": [
      {
        "feature": "Software Delay Loop",
        "description": "The software delay loop with registers r18 and r19 has been removed.",
        "impact": "This change could potentially improve performance and efficiency by offloading timing to hardware."
      }
    ],
    "behavioral_changes": [
      {
        "change": "LED Blinking Method",
        "old_behavior": "The LED was blinked using a software delay loop.",
        "new_behavior": "The LED is now blinked using a hardware timer.",
        "security_impact": "No direct security impact."
      }
    ],
    "change_summary": {
      "total_changes": 3,
      "major_changes": [
        "Replacement of software delay loop with hardware timer",
        "Introduction of EOR instruction for LED toggling"
      ],
      "risk_level": "low"
    },
    "recommendations": [
      "Ensure compatibility with hardware Timer0",
      "Test the new EOR instruction for LED toggling"
    ],
    "analysis_metadata": {
      "old_doc_length": 326,
      "new_doc_length": 631,
      "total_differences": 3,
      "new_features_count": 2,
      "removed_features_count": 1,
      "behavioral_changes_count": 1,
      "analysis_method": "llm_based"
    }
  }
}
```

## Output

```json
{
  "success": true,
  "compliance_status": "compliant",
  "mismatches": [],
  "matches": [
    {
      "description": "The firmware version and functionality update is reflected in both the code and documentation.",
      "code_reference": "line_number: 1, change_type: modified",
      "doc_reference": "section: Behavior, change_type: modified"
    },
    {
      "description": "The removal of LED control and delay loop is reflected in both the code and documentation.",
      "code_reference": "line_number: 17, change_type: removed",
      "doc_reference": "section: Implementation Notes, change_type: removed"
    },
    {
      "description": "The addition of Timer0 setup, timer counter reading, and timer reset is reflected in both the code and documentation.",
      "code_reference": "line_number: 17, 20, 24, change_type: added",
      "doc_reference": "section: Key Differences from v1, change_type: added"
    }
  ],
  "compliance_score": 1.0,
  "summary": {
    "total_code_changes": 6,
    "total_doc_changes": 3,
    "matched_changes": 3,
    "unmatched_changes": 0,
    "overall_assessment": "The code changes match perfectly with the documentation changes. There are no mismatches found."
  },
  "recommendations": [
    "Continue maintaining the high level of compliance between code and documentation.",
    "Consider adding more detailed explanations in the documentation for major changes."
  ],
  "analysis_metadata": {
    "code_changes_count": 6,
    "spec_changes_count": 3,
    "mismatches_count": 0,
    "matches_count": 3,
    "analysis_method": "llm_based"
  }
}
```
