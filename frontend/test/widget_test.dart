// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/main.dart';

void main() {
  testWidgets('Translation page renders correctly', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const XPTranslatorApp());

    // Verify that the app title is displayed
    expect(find.text('XP Translator'), findsOneWidget);
    
    // Verify that input field is present
    expect(find.text('输入中文文本'), findsOneWidget);
    
    // Verify that translate button is present
    expect(find.text('翻译'), findsOneWidget);
    
    // Verify that clear button is present
    expect(find.text('清空'), findsOneWidget);
  });

  testWidgets('Settings dialog can be opened', (WidgetTester tester) async {
    await tester.pumpWidget(const XPTranslatorApp());
    
    // Tap the settings icon
    await tester.tap(find.byIcon(Icons.settings));
    await tester.pumpAndSettle();
    
    // Verify settings dialog is shown
    expect(find.text('设置'), findsOneWidget);
    expect(find.text('后端 API 地址'), findsOneWidget);
  });
}
