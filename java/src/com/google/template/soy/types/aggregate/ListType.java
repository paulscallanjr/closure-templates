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

package com.google.template.soy.types.aggregate;

import com.google.common.base.Objects;
import com.google.common.base.Preconditions;
import com.google.template.soy.data.SoyList;
import com.google.template.soy.data.SoyValue;
import com.google.template.soy.types.SoyType;

/**
 * Represents the type of a list, a sequential random-access container keyed
 * by integer.
 *
 * <p> Important: Do not use outside of Soy code (treat as superpackage-private).
 *
 */
public class ListType implements SoyType {


  private final SoyType elementType;


  private ListType(SoyType elementType) {
    Preconditions.checkNotNull(elementType);
    this.elementType = elementType;
  }


  public static ListType of(SoyType elementType) {
    return new ListType(elementType);
  }


  @Override public Kind getKind() {
    return Kind.LIST;
  }


  public SoyType getElementType() {
    return elementType;
  }


  @Override public boolean isAssignableFrom(SoyType srcType) {
    if (srcType.getKind() == Kind.LIST) {
      ListType srcListType = (ListType) srcType;
      // Lists are covariant (because values are immutable.)
      return elementType.isAssignableFrom(srcListType.elementType);
    }
    return false;
  }


  @Override public boolean isInstance(SoyValue value) {
    return value instanceof SoyList;
  }


  @Override public String toString() {
    return "list<" + elementType + ">";
  }


  @Override public boolean equals(Object other) {
    return other != null &&
        this.getClass() == other.getClass() &&
        ((ListType) other).elementType.equals(elementType);
  }


  @Override public int hashCode() {
    return Objects.hashCode(this.getClass(), elementType);
  }
}
