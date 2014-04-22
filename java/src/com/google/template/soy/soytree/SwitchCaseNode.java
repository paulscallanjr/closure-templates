/*
 * Copyright 2008 Google Inc.
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

package com.google.template.soy.soytree;

import com.google.common.collect.Lists;
import com.google.template.soy.base.SoySyntaxException;
import com.google.template.soy.exprparse.ExprParseUtils;
import com.google.template.soy.exprtree.ExprRootNode;
import com.google.template.soy.soytree.SoyNode.ConditionalBlockNode;
import com.google.template.soy.soytree.SoyNode.ExprHolderNode;

import java.util.List;


/**
 * Node representing a 'case' block in a 'switch' block.
 *
 * <p> Important: Do not use outside of Soy code (treat as superpackage-private).
 *
 */
public class SwitchCaseNode extends CaseOrDefaultNode
    implements ConditionalBlockNode, ExprHolderNode {


  /** The text for this case's expression list. */
  private final String exprListText;

  /** The parsed expression list. */
  private final List<ExprRootNode<?>> exprList;


  /**
   * @param id The id for this node.
   * @param commandText The command text.
   * @throws SoySyntaxException If a syntax error is found.
   */
  public SwitchCaseNode(int id, String commandText) throws SoySyntaxException {
    super(id, "case", commandText);

    exprListText = commandText;
    exprList = ExprParseUtils.parseExprListElseThrowSoySyntaxException(
        exprListText, "Invalid expression list in 'case' command text \"" + commandText + "\".");
  }


  /**
   * Copy constructor.
   * @param orig The node to copy.
   */
  protected SwitchCaseNode(SwitchCaseNode orig) {
    super(orig);
    this.exprListText = orig.exprListText;
    this.exprList = Lists.newArrayListWithCapacity(orig.exprList.size());
    for (ExprRootNode<?> origExpr : orig.exprList) {
      this.exprList.add(origExpr.clone());
    }
  }


  @Override public Kind getKind() {
    return Kind.SWITCH_CASE_NODE;
  }


  /** Returns the text for this case's expression list. */
  public String getExprListText() {
    return exprListText;
  }


  /** Returns the parsed expression list, or null if the expression list is not in V2 syntax. */
  public List<ExprRootNode<?>> getExprList() {
    return exprList;
  }


  @Override public List<ExprUnion> getAllExprUnions() {
    return ExprUnion.createList(exprList);
  }


  @Override public SwitchCaseNode clone() {
    return new SwitchCaseNode(this);
  }

}
