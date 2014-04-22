/*
 * Copyright 2013 Google Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.google.template.soy.basicfunctions;

import com.google.common.base.Preconditions;
import com.google.common.collect.ImmutableSet;
import com.google.inject.Inject;
import com.google.inject.Singleton;
import com.google.template.soy.data.SanitizedContent;
import com.google.template.soy.data.SoyValue;
import com.google.template.soy.data.restricted.IntegerData;
import com.google.template.soy.data.restricted.StringData;
import com.google.template.soy.jssrc.restricted.JsExpr;
import com.google.template.soy.jssrc.restricted.JsExprUtils;
import com.google.template.soy.jssrc.restricted.SoyJsSrcFunction;
import com.google.template.soy.shared.restricted.SoyJavaFunction;
import com.google.template.soy.shared.restricted.SoyPureFunction;

import java.util.List;
import java.util.Set;


/**
 * A function that determines the length of a string.
 *
 * <p><code>strLen(expr1)</code> requires <code>expr1</code> to be of type
 * string or {@link com.google.template.soy.data.SanitizedContent}.
 *
 */
@Singleton
@SoyPureFunction
class StrLenFunction implements SoyJavaFunction, SoyJsSrcFunction {


  @Inject
  StrLenFunction() {}


  @Override public String getName() {
    return "strLen";
  }


  @Override public Set<Integer> getValidArgsSizes() {
    return ImmutableSet.of(1);
  }


  @Override public SoyValue computeForJava(List<SoyValue> args) {
    SoyValue arg0 = args.get(0);

    Preconditions.checkArgument(arg0 instanceof StringData || arg0 instanceof SanitizedContent,
        "First argument to strLen() function is not StringData or SanitizedContent: %s", arg0);

    return IntegerData.forValue(arg0.coerceToString().length());
  }


  @Override public JsExpr computeForJsSrc(List<JsExpr> args) {
    // Coerce SanitizedContent args to strings.
    String arg0 = JsExprUtils.toString(args.get(0)).getText();

    return new JsExpr("(" + arg0 + ").length", Integer.MAX_VALUE);
  }

}
